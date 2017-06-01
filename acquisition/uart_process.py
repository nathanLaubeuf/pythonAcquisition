# Example of interaction with a BLE UART device using a UART service
# implementation.
# Author: Tony DiCola
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services.uart import UART
import socket
import time
import signal
import sys

# /!\ Only works in python2.7
# Try to make exit more graceful : http://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()


# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.
def main():

    data = []
    dataflow = ""
    notFound = True

    ###############################################################################
    #                                  Socket init
    ###############################################################################

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 12000)
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)

    ###############################################################################
    #                                  BLE init
    ###############################################################################

    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

    # Scan for UART devices.
    print('Searching for UART device...')
    try:
        adapter.start_scan()
        # Search for the first UART device found (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        while notFound:  # Only connects to desired device
            devices = UART.find_devices()
            for deviceIter in devices:
                if deviceIter.name == "Adafruit Bluefruit LE":
                    notFound = False
                    device = deviceIter
        if device is None:
            raise RuntimeError('Failed to find UART device!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print('Connecting to device...')
    device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
    # to change the timeout.

    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the UART service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        print('Discovering services...')
        UART.discover(device)

        # Once service discovery is complete create an instance of the service
        # and start interacting with it.
        uart = UART(device)

        # Write a string to the TX characteristic.
        uart.write('START')
        print("Sent 'START' to the device.")

        # Now wait up to one minute to receive data from the device.
        print('Waiting up to 60 seconds to receive data from the device...')
        received = uart.read(timeout_sec=60)
        while received is not None:
            print('Received: {0}'.format(received))
            sock.sendall(received)
            received = uart.read(timeout_sec=60)
        print('End of transmission')

    finally:
        # Make sure device is disconnected on exit.
        uart.write('STOP')
        print("Sent 'STOP' to the device.")
        time.sleep(1)
        uart.write('STOP')
        print("Sent 'STOP' to the device.")
        time.sleep(1)
        print('closing socket')
        sock.close()
        time.sleep(1)
        print('Disconnecting device')
        device.disconnect()


# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
