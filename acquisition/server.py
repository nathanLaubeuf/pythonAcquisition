import sys
import socket
import time
from random import random
from queue import Queue
from PyQt5.QtCore import (QObject, QThread, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QApplication)


class Server(QObject):
    """
    Producer thread
    This thread will receive data from the board and emit a signal when new data is available
    """
    data_read = pyqtSignal(bytes)
    finished = pyqtSignal()
    sock = None
    server_address = None
    dataList = []
    dataflow = ""
    dataSend = []

    def __init__(self):
        super().__init__()
        self.server_address = ('localhost', 10000)
        self.dataList = []
        self.dataflow = ""
        self.dataSend = []

    @pyqtSlot()
    def process(self):
        print('starting up on %s port %s' % self.server_address)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        self.sock.listen()

        while True:
            print('waiting for a connection')
            connection, client_address = self.sock.accept()
            try:
                print('connection from', client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(20)
                    print('received "%s"' % data)
                    if data:
                        print('recived data')
                        self.dataflow += data.decode("utf-8")
                        while len(dataflow) > 12:
                            print('Buffered: {0}'.format(dataflow))
                            self.dataList = dataflow.split(' ')
                            print(self.dataList)
                            self.dataSend = self.dataList.pop(0).split("|")
                            print("Value : {0}".format(self.dataList.pop(0)))
                            dataflow = " ".join(self.dataList)
                    else:
                        print('no more data from', client_address)
                        break

            finally:
                # Clean up the connection
                connection.close()



class Dummy_Client(QObject):

    sock = None
    finished = pyqtSignal()
    server_address = ('localhost', 10000)


    def __init__(self):
        super().__init__()

    def process(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)
        try:

            # Send data
            message = ('AAAAAAAAAAAAAAA').encode('utf-8')
            print('sending "%s"' % message)
            self.sock.sendall(message)

        finally:
            print('closing socket')
            self.sock.close()
            self.finished.emit()

@pyqtSlot(bytes)
def handle(next_value):
    """Test handler"""
    print("sent to gui : %s" % str(next_value))

if __name__ == "__main__":
    app = QApplication(sys.argv)  # define a Qt application

    thread_serv = QThread()
    thread_cli = QThread()
    producer = Server()
    client = Dummy_Client()

    producer.moveToThread(thread_serv)
    thread_serv.started.connect(producer.process)
    producer.finished.connect(thread_serv.quit)
    producer.finished.connect(producer.deleteLater)
    thread_serv.finished.connect(thread_serv.deleteLater)

    producer.data_read.connect(handle)

    time.sleep(1)

    client.moveToThread(thread_cli)
    thread_cli.started.connect(client.process)
    client.finished.connect(thread_cli.quit)
    client.finished.connect(client.deleteLater)
    thread_cli.finished.connect(thread_cli.deleteLater)

    thread_serv.start()
    thread_cli.start()

    sys.exit(app.exec_())