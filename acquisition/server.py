import sys
import socket
import time

from struct import *

from random import random
from queue import Queue
from PyQt5.QtCore import (QObject, QThread, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QApplication)


# --  Benchmarking -- #
# current_milli_time = lambda: int(round(time.time() * 1000))
# ------------------  #

class Server(QObject):
    """
    Producer thread
    This thread will receive data from the board and emit a signal when new data is available
    """
    data_read = pyqtSignal(list)
    finished = pyqtSignal()
    sock = None
    server_address = None
    raw_data = b''
    state = 0
    polar_0_data = []
    polar_1_data = []
    voltage_Value = []
    res_Value = .0
    R0_val = 1600.0

    # --  Benchmarking -- #
    # prev_time = cur_time = 0
    # ------------------  #


    def __init__(self):
        super().__init__()
        self.server_address = ('localhost', 12000)

    def get_raw_value(self, expected):
        """
        Unformats the data received through the link

        The format is divided in 2 parts :
        bit 0 to 5 are the header, bit 6 to 15 are the data

        bit 0: polarity of the power supply
        bit 1: header parity bit
        bit 2 to 5: channel number
        bit 6 to 15: data

        Also checks for errors an manage the finite state machine
        """
        temp = 0
        # print(self.state)
        if len(self.raw_data) == 2:
            temp = unpack('!H', self.raw_data[:2])[0]
            # print('data : {}'.format(temp >> 10))
            if temp >> 10 == expected:
                if expected < 30:
                    self.polar_0_data.append(temp & 1023)
                else:
                    self.polar_1_data.append(temp & 1023)
                # print(bin(temp >> 10))

                if self.state == 7 or self.state == 19:
                    self.state = 0
                else:
                    self.state += 1
                self.raw_data = b''
            else:
                print("Error")
                self.polar_0_data = []
                self.polar_1_data = []
                if temp & 252 == 0:
                    self.state = 1
                    self.raw_data = bytes([self.raw_data[1]])
                elif temp & 252 == 48:
                    self.state = 13
                    self.raw_data = bytes([self.raw_data[1]])
                else:
                    self.state = 0
                    self.raw_data = b''
        else:
            return

    def send_ready_res(self):
        """
        Compute and sent the resistances values when enough values are available
        """
        if len(self.polar_0_data) == 7:
            """ 
            Buffer of positive polarity complete :
            Resistance are computed for all 10 channels
            """
            # print('1')
            # print(self.polar_0_data[:-2])
            # print(self.polar_0_data[-2:])

            volt_max = max(self.polar_0_data[-2:])
            volt_min = min(self.polar_0_data[-2:])
            try:
                self.voltage_Value = [(elt - volt_min) / (volt_max - volt_min) for elt in
                                      self.polar_0_data[:-2]]
            except ZeroDivisionError:
                print("/!\ WARNING : Equal GPIO voltages")
                self.voltage_Value = [0.0 for elt in self.polar_0_data[:-2]]

            try:
                self.res_Value = [round(self.R0_val * (1 / volt - 1), 1) for volt in
                                  self.voltage_Value]
                # print(self.res_Value)

            except ZeroDivisionError:
                print("Polar 0 ZeroDivisionError")
                self.res_Value = []
                for i in range(len(self.voltage_Value)):
                    if self.voltage_Value[i] == 0.0:
                        self.res_Value.append(round(self.R0_val * 100, 1))
                    else:
                        self.res_Value.append(round(self.R0_val * (1 / self.voltage_Value[i] - 1), 1))
            # print(self.res_Value)
            self.data_read.emit(self.res_Value)
            self.polar_0_data = []

            # --  Benchmarking -- #
            # self.cur_time = current_milli_time()
            # print(self.cur_time - self.prev_time)
            # self.prev_time = self.cur_time
            # ------------------  #

        elif len(self.polar_1_data) == 7:
            """ 
            Buffer of negative polarity complete :
            Resistance are computed for all 10 channels
            """
            # print('2')
            # print(self.polar_1_data[:-2])
            # print(self.polar_1_data[-2:])
            volt_max = max(self.polar_1_data[-2:])
            volt_min = min(self.polar_1_data[-2:])
            try:
                self.voltage_Value = [(elt - volt_min) / (volt_max - volt_min) for elt in
                                      self.polar_1_data[:-2]]
            except ZeroDivisionError:
                print("/!\ WARNING : Equal GPIO voltages")
                self.voltage_Value = [0.0 for elt in self.polar_1_data[:-2]]
            try:
                self.res_Value = [round(self.R0_val / (1 / volt - 1), 1) for volt in
                                  self.voltage_Value]
            except ZeroDivisionError:
                print("Polar 1 ZeroDivisionError")
                self.res_Value = []
                for i in range(len(self.voltage_Value)):
                    if self.voltage_Value[i] == 1.0 or self.voltage_Value[i] == 0.0:
                        self.res_Value.append(round(self.R0_val * 100, 1))
                    else:
                        self.res_Value.append(round(self.R0_val / (1 / self.voltage_Value[i] - 1), 1))
            # print(self.res_Value)
            self.data_read.emit(self.res_Value)
            self.polar_1_data = []

            # --  Benchmarking -- #
            # self.cur_time = current_milli_time()
            # print(self.cur_time - self.prev_time)
            # self.prev_time = self.cur_time
            # ------------------  #

    @pyqtSlot()
    def process(self):
        """Main process with actual server functions"""
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

                while True:
                    data = connection.recv(1)
                    # print('received "%s"' % data)
                    if data:
                        """
                        Finite state machine :
                        Each state correspond to a specific header 
                        except state 0 which detect the beginning of a frame A0, A1, etc.
                        State 12 and state 24 return to state 0
                        """
                        # detect the starting point
                        if (unpack('!B', data)[0] >> 2) == 0 and self.state == 0:
                            self.raw_data += data
                            self.state = 1
                        elif (unpack('!B', data)[0] >> 2) == 48 and self.state == 0:
                            self.raw_data += data
                            self.state = 13

                        elif self.state == 1:
                            self.raw_data += data
                            self.get_raw_value(0)
                        elif self.state == 2:
                            self.raw_data += data
                            self.get_raw_value(17)
                        elif self.state == 3:
                            self.raw_data += data
                            self.get_raw_value(18)
                        elif self.state == 4:
                            self.raw_data += data
                            self.get_raw_value(3)
                        elif self.state == 5:
                            self.raw_data += data
                            self.get_raw_value(20)
                        elif self.state == 6:
                            self.raw_data += data
                            self.get_raw_value(5)
                        elif self.state == 7:
                            self.raw_data += data
                            self.get_raw_value(6)
                        # elif self.state == 8:
                        #     self.raw_data += data
                        #     self.get_raw_value(23)
                        # elif self.state == 9:
                        #     self.raw_data += data
                        #     self.get_raw_value(24)
                        # elif self.state == 10:
                        #     self.raw_data += data
                        #     self.get_raw_value(9)
                        # elif self.state == 11:
                        #     self.raw_data += data
                        #     self.get_raw_value(10)
                        # elif self.state == 12:
                        #     self.raw_data += data
                        #     self.get_raw_value(27)

                        elif self.state == 13:
                            self.raw_data += data
                            self.get_raw_value(48)
                        elif self.state == 14:
                            self.raw_data += data
                            self.get_raw_value(33)
                        elif self.state == 15:
                            self.raw_data += data
                            self.get_raw_value(34)
                        elif self.state == 16:
                            self.raw_data += data
                            self.get_raw_value(51)
                        elif self.state == 17:
                            self.raw_data += data
                            self.get_raw_value(36)
                        elif self.state == 18:
                            self.raw_data += data
                            self.get_raw_value(53)
                        elif self.state == 19:
                            self.raw_data += data
                            self.get_raw_value(54)
                        # elif self.state == 20:
                        #     self.raw_data += data
                        #     self.get_raw_value(39)
                        # elif self.state == 21:
                        #     self.raw_data += data
                        #     self.get_raw_value(40)
                        # elif self.state == 22:
                        #     self.raw_data += data
                        #     self.get_raw_value(57)
                        # elif self.state == 23:
                        #     self.raw_data += data
                        #     self.get_raw_value(58)
                        # elif self.state == 24:
                        #     self.raw_data += data
                        #     self.get_raw_value(43)

                        self.send_ready_res()
                    else:
                        print('no more data from', client_address)
                        break

            finally:
                # Clean up the connection
                connection.close()


class Dummy_Client(QObject):
    "Test client : /!\ not working in current version"
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
    # thread_cli = QThread()
    producer = Server()
    # client = Dummy_Client()

    producer.moveToThread(thread_serv)
    thread_serv.started.connect(producer.process)
    producer.finished.connect(thread_serv.quit)
    producer.finished.connect(producer.deleteLater)
    thread_serv.finished.connect(thread_serv.deleteLater)

    producer.data_read.connect(handle)

    time.sleep(1)

    # client.moveToThread(thread_cli)
    # thread_cli.started.connect(client.process)
    # client.finished.connect(thread_cli.quit)
    # client.finished.connect(client.deleteLater)
    # thread_cli.finished.connect(thread_cli.deleteLater)

    thread_serv.start()
    # thread_cli.start()

    sys.exit(app.exec_())
