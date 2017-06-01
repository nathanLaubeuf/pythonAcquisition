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
    data_read = pyqtSignal(list)
    finished = pyqtSignal()
    sock = None
    server_address = None
    dataList = []
    dataflow = ""
    dataSend = []
    voltage_Value = .0
    res_Value = .0
    R0_val = 1200.0

    def __init__(self):
        super().__init__()
        self.server_address = ('localhost', 12000)
        self.dataList = []
        self.dataflow = ""
        self.dataSend = []

    @pyqtSlot()
    def process(self):

        datum = ""

        print('starting up on %s port %s' % self.server_address)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        self.sock.listen()
        while True:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = self.sock.accept()
            try:
                print('connection from', client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(40)
                    # print('received "%s"' % data)
                    if data:
                        # print('received data')
                        try:
                            self.dataflow += data.decode("utf-8")
                            while len(self.dataflow) > 32:
                                #print('Buffered: {0}'.format(self.dataflow))
                                self.dataList = self.dataflow.split(' ')
                                # print(self.dataList)
                                try:
                                    datum = self.dataList.pop(0)
                                    volt_min = 0
                                    volt_max = 4095
                                    self.dataSend = datum.split("|")
                                    self.dataSend = list(map(int, self.dataSend))
                                    print("Value : {0}".format(self.dataSend))
                                    volt_max = max(self.dataSend[-2:])
                                    volt_min = min(self.dataSend[-2:])
                                    try:
                                        # elts = [elt/2 + 1241 for elt in self.dataSend[1:4]]
                                        self.voltage_Value = [(elt - volt_min)/(volt_max - volt_min) for elt in self.dataSend[1:-2]]
                                        if self.dataSend.pop(0) == 0:
                                            # self.voltage_Value = [elt / 1023 for elt in self.dataSend]
                                            self.res_Value = [round(self.R0_val * (1 / volt - 1), 1) for volt in
                                                              self.voltage_Value]
                                        else:
                                            # self.voltage_Value = [(1023 - elt) / 1023 for elt in self.dataSend]
                                            self.res_Value = [round(self.R0_val * (volt / (1 - volt)), 1) for volt in
                                                          self.voltage_Value]

                                    except ZeroDivisionError:
                                        self.res_Value = [round(self.R0_val * (1 / (volt + 0.1) - 1), 1) for volt in
                                                          self.voltage_Value]
                                    # print("Volt : {0}".format(self.voltage_Value))
                                    # print("Resistance : {0}".format(self.res_Value))
                                    self.data_read.emit(self.res_Value)

                                except ValueError:
                                    print("Value Error")
                                except IndexError:
                                    print("IndexError")
                                finally:
                                    self.dataflow = " ".join(self.dataList)
                        except UnicodeDecodeError:
                            print("UnicodeDecodeError")

                    else:
                        print('no more data from', client_address)
                        break

            finally:
                # Clean up the connection
                connection.close()



class Dummy_Client(QObject):

    sock = None
    finished = pyqtSignal()
    server_address = ('localhost', 12000)


    def __init__(self):
        super().__init__()

    def process(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)
        try:

            # Send data
            message = (' 123|123 123|123 123|123').encode('utf-8')
            print('sending "%s"' % message)
            self.sock.sendall(message)

        finally:
            print('closing socket')
            self.sock.close()
            self.finished.emit()

@pyqtSlot(list)
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
