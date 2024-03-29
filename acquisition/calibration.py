from PyQt5.QtCore import (QObject, pyqtSlot, pyqtSignal, QThread)
from PyQt5.QtWidgets import (QApplication)
from serial import *
from threading import Timer
import csv



class ExCaliber(QObject):
    calib_stopped = pyqtSignal()
    new_angle = pyqtSignal(float)

    def __init__(self):
        super().__init__()

        self.thread = None
        self.ser_conn = None
        self.angle = None
        self.channel = 0
        self.file_name = 'calibrations/calibration_0.csv'
        self.calib_serial = ''
        self.file = None
        self.writer = None

    @pyqtSlot()
    def start_calib(self):
        self.angle = None
        print('Start calibration')
        self.file = open(self.file_name, 'w')
        self.writer = csv.writer(self.file, delimiter=';',
                                          quotechar='|', quoting=csv.QUOTE_MINIMAL)

    @pyqtSlot()
    def stop_calib(self):
        print('Stop calib')
        # try:
        #     self.ser_conn.data_read.disconnect(self.imu_angle_handle)
        # except RuntimeError:
        #     print('Serial connection already closed')
        self.file.close()
        # app.quit() # Uncomment for a non locking example

    @pyqtSlot(float)
    def imu_angle_handle(self, angle):
        self.angle = angle
        self.new_angle.emit(angle)
        # print("angle = {}".format(angle))

    @pyqtSlot(list)
    def stretch_res_handle(self, res):
        if self.angle is not None:
            angle_vs_res = self.angle, res[self.channel]
            print(angle_vs_res)
            self.writer.writerow(angle_vs_res)

    @pyqtSlot(int)
    def channel_change(self, chan):
        self.file_name = "calibrations/calibrations_{}.csv".format(chan)
        self.channel = chan

    @pyqtSlot(str)
    def set_calib_serial(self, serial_name):
        if self.thread is not None:
            self.ser_conn.stop_serial()

        self.calib_serial = serial_name
        self.thread = QThread()
        self.ser_conn = SerialCon(self.calib_serial)
        self.ser_conn.moveToThread(self.thread)
        self.thread.started.connect(self.ser_conn.process)
        self.ser_conn.finished.connect(self.thread.quit)
        self.ser_conn.finished.connect(self.ser_conn.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.ser_conn.no_serial.connect(self.propagate_no_serial)
        self.ser_conn.data_read.connect(self.imu_angle_handle)
        self.thread.start()


    @pyqtSlot()
    def propagate_no_serial(self):
        self.calib_serial = ''
        self.calib_stopped.emit()


class SerialCon(QObject):

    data_read = pyqtSignal(float)
    finished = pyqtSignal()
    no_serial = pyqtSignal()
    calib_serial = ''
    run = True

    def __init__(self, serial_name):
        super().__init__()
        self.calib_serial = serial_name

    def start_serial(self):
        print('Start Serial')
        try:
            self.ser = Serial(self.calib_serial, 38400, timeout=5)  # open serial port
        except SerialException:
            self.no_serial.emit()
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
        try:
            self.start_serial()
            while self.run:
                try:
                    line = self.ser.readline()
                except OSError:
                    print('Serial disconnected')
                    self.no_serial.emit()
                    break
                if len(line) != 0:
                    # print(float(line))
                    self.data_read.emit(float(line))
            self.ser.close()
            print('Serial closed')
        except AttributeError:
            self.no_serial.emit()
        self.finished.emit()
        return



if __name__ == "__main__":
    app = QApplication(sys.argv)  # define a Qt application
    calib = ExCaliber()
    t = Timer(10.0, calib.stop_calib)
    calib.start_calib()
    t.start()
    sys.exit(app.exec_())