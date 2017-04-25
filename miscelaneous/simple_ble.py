import select
import socket
import sys

import objc
from PyObjCTools import AppHelper

"""
    Recives data through a local host socket and send them to a ble device 
"""

objc.loadBundle("CoreBluetooth", globals(),
    bundle_path=objc.pathForFramework(u'/System/Library/Frameworks/IOBluetooth.framework/Versions/A/Frameworks/CoreBluetooth.framework'))

nrf51_service = CBUUID.UUIDWithString_(u'6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
nrf51_rx = CBUUID.UUIDWithString_(u'6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
nrf51_tx = CBUUID.UUIDWithString_(u'6E400002-B5A3-F393-E0A9-E50E24DCCA9E')

class RobotDelegate(object):
    """Delegate class of my central manager"""
    def __init__(self):
        self.manager = None
        self.peripheral = None

        self.service = None

        self.rx = None
        self.tx = None

        self.comms = None
    """
    ------------------------------------------------------------------------------------
        From the CBCentralManagerDelegate protocol
    ------------------------------------------------------------------------------------
    """
    def centralManagerDidUpdateState_(self, manager):
        """Invoked when the central manager s state is updated."""
        print(repr(manager), "done it!")
        self.manager = manager
        manager.scanForPeripheralsWithServices_options_([nrf51_service], None)

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        """Invoked when the central manager discovers a peripheral while scanning."""
        self.peripheral = peripheral
        manager.connectPeripheral_options_(peripheral, None)

    def centralManager_didConnectPeripheral_(self, manager, peripheral):
        """Invoked when a connection is successfully created with a peripheral."""
        print(repr(peripheral))
        self.peripheral.setDelegate_(self)
        self.peripheral.discoverServices_([nrf51_service])

    def centralManager_didFailToConnectPeripheral_error_(self, manager, peripheral, error):
        """Invoked when the central manager fails to create a connection with a peripheral."""
        print(repr(error))

    def centralManager_didDisconnectPeripheral_error_(self, manager, peripheral, error):
        """Invoked when an existing connection with a peripheral is torn down."""
        print(repr(error))
        AppHelper.stopEventLoop()

    """
    ------------------------------------------------------------------------------------
        From the CBPeripheralDelegate protocol
    ------------------------------------------------------------------------------------
    """

    def peripheral_didDiscoverServices_(self, peripheral, services):
        """Invoked when you discover the peripheral s available services."""
        self.service = self.peripheral.services()[0]
        self.peripheral.discoverCharacteristics_forService_([nrf51_rx, nrf51_tx], self.service)

    def peripheral_didDiscoverCharacteristicsForService_error_(self, peripheral, service, error):
        """Invoked when you discover the characteristics of a specified service."""
        print(repr(service))
        print(repr(error))

        for characteristic in self.service.characteristics():
            if characteristic.UUID() == nrf51_rx:
                self.rx = characteristic
                self.peripheral.setNotifyValue_forCharacteristic_(True, self.rx)
            elif characteristic.UUID() == nrf51_tx:
                self.tx = characteristic

        print(repr(self.rx.UUID()))
        print(repr(self.tx.UUID()))

    def peripheral_didWriteValueForCharacteristic_error_(self, peripheral, characteristic, error):
        """Invoked when you write data to a characteristic s value."""
        print(repr(error))

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self, peripheral, characteristic, error):
        """
        Invoked when the peripheral receives a request to start or stop providing notifications for a specified
        characteristic s value.
        """
        print("Receiving notifications")

    def peripheral_didUpdateValueForCharacteristic_error_(self, peripheral, characteristic, error):
        """
        Invoked when you retrieve a specified characteristic s value, or when the peripheral device notifies
        your app that the characteristic s value has changed.
        """
        self.comms.send(characteristic.value().bytes().tobytes())
        print(repr(characteristic.value().bytes().tobytes()))

    """
    ------------------------------------------------------------------------------------
        shutdown and send method
    ------------------------------------------------------------------------------------
    """

    def shutdown(self):
        if self.peripheral is not None:
            self.manager.cancelPeripheralConnection_(self.peripheral)
        else:
            AppHelper.stopEventLoop()

    def send(self, byte):
        """ Writes a byte in the tx characteristic of the nrf51 service"""
        byte = NSData.dataWithBytes_length_(byte, 1)
        self.peripheral.writeValue_forCharacteristic_type_(byte, self.tx, 0) # Writes the value of a characteristic.


class CommsManager(object):
    def __init__(self, robot):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 9999))
        self.listener.listen(1)

        self.connection = None

        self.robot = robot
        self.robot.comms = self

    def loop(self):
        endpoints = [sys.stdin, self.listener] # list of connections
        if self.connection is not None:
            endpoints.append(self.connection)

        r, w, e = select.select(endpoints, [], [], 0)
        if sys.stdin in r:
            delegate.shutdown()
            return
        if self.listener in r:
            self.connection, _ = self.listener.accept()
        if self.connection in r:
            c = self.connection.recv(1)
            if len(c) == 0:
                print("closed")
                self.connection.close()
                self.connection = None
            elif c not in ('\r', '\n'):
                print(repr(c))
                self.robot.send(c)

        AppHelper.callLater(0.1, self.loop)

    def send(self, data):
        """
        send data to localhost
        not used here
        """
        while len(data):
            sent = self.connection.send(data)
            data = data[sent:]

delegate = RobotDelegate()
manager = CBCentralManager.alloc()
manager.initWithDelegate_queue_options_(delegate, None, None)

comms = CommsManager(delegate)

print(repr(manager))

AppHelper.callLater(0.1, comms.loop)
AppHelper.runConsoleEventLoop()
