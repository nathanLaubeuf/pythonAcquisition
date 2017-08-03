from PyQt5.QtCore import (QObject, pyqtSlot, pyqtSignal, QThread)
from PyQt5.QtWidgets import (QApplication)
from serial import *
from threading import Timer
import csv

class ExCaliber(QObject):

    def __init__(self):
        super().__init__()

        self.thread = None
        self.ser_conn = None
        self.angle = None
        self.channel = 0
        self.file_name = 'calibration.csv'
        self.file = None
        self.writer = None

    @pyqtSlot()
    def start_calib(self):
        self.thread = QThread()
        self.ser_conn = SerialCon()
        self.ser_conn.moveToThread(self.thread)
        self.thread.started.connect(self.ser_conn.process)
        self.ser_conn.finished.connect(self.thread.quit)
        self.ser_conn.finished.connect(self.ser_conn.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.ser_conn.data_read.connect(self.imu_angle_handle)
        self.angle = None
        print('Start calibration')
        if os.path.isfile(self.file_name):
            raise FileExistsError
        else:
            self.file = open(self.file_name, 'w')
            self.writer = csv.writer(self.file, delimiter=';',
                                     quotechar='|', quoting=csv.QUOTE_MINIMAL)
        self.thread.start()

    @pyqtSlot()
    def stop_calib(self):
        print('Stop calib')
        self.ser_conn.stop_serial()
        self.file.close()
        # app.quit() # Uncomment for a non locking example

    @pyqtSlot(float)
    def imu_angle_handle(self, angle):
        self.angle = angle
        # print("angle = {}".format(angle))

    @pyqtSlot(list)
    def stretch_res_handle(self, res):
        if self.angle is not None:
            angle_vs_res = self.angle, res[self.channel]
            print(angle_vs_res)
            self.writer.writerow(angle_vs_res)

    @pyqtSlot(int)
    def channel_change(self, chan):
        self.channel = chan


class SerialCon(QObject):

    data_read = pyqtSignal(float)
    finished = pyqtSignal()
    run = True

    def __init__(self):
        super().__init__()

    def start_serial(self):
        print('Start Serial')
        try:
            self.ser = Serial('/dev/cu.usbmodem1421', 38400, timeout=5)  # open serial port
        except self.ser.SerialException as e:
            print("could not open serial port '{}': {}".format('/dev/cu.usbmodem1421', e))
        print(self.ser.name)  # check which port was really used

        if self.ser.is_open:
            self.ser.close()
            self.ser.open()
        else:
            self.ser.open()

    def stop_serial(self):
        self.run = False


    @pyqtSlot()
    def process(self):
        self.start_serial()
        while self.run:
            line = self.ser.readline()
            if len(line) != 0:
                # print(float(line))
                self.data_read.emit(float(line))


        self.ser.close()
        print('Serial closed')
        self.finished.emit()
        return



if __name__ == "__main__":
    app = QApplication(sys.argv)  # define a Qt application
    calib = ExCaliber()
    t = Timer(10.0, calib.stop_calib)
    calib.start_calib()
    t.start()
    sys.exit(app.exec_())
