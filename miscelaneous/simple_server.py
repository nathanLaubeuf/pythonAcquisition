import socket
import sys

dataList = []
dataflow = ""
dataSend = []
datum = ""

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(20)
            print('received "%s"' % data)
            if data:
                print('recived data')
                try:
                    dataflow += data.decode("utf-8")
                    while len(dataflow) > 12:
                        print('Buffered: {0}'.format(dataflow))
                        dataList = dataflow.split(' ')
                        print(dataList)
                        try:
                            datum = dataList.pop(0)
                            dataSend = datum.split("|")
                            dataSend = list(map(int, dataSend))
                            print("Value : {0}".format(dataSend))

                        except ValueError :
                            print("Value Error")
                        finally:
                            dataflow = " ".join(dataList)
                except UnicodeDecodeError:
                    print("UnicodeDecodeError")

            else:
                print('no more data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
