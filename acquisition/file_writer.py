import sys
import os.path
import csv
from PyQt5.QtCore import (pyqtSlot, QObject, QThread, pyqtSignal)


class FileWritter(QObject):

    makeFileNameSig = pyqtSignal()
    patientNum = 0
    sessionNum = 0
    testNum = 0
    workDir = None
    fileName = None
    file = None
    writer = None

    def __init__(self):
        super().__init__()
        self.makeFileNameSig.connect(self.makeFileName)

    @pyqtSlot()
    def makeFileName(self):
        try:
            self.fileName = self.workDir + '/' + str(self.patientNum) + '_' + str(self.sessionNum) + '_' + str(self.testNum) + ".csv"
        except TypeError:
            self.fileName = str(self.patientNum) + str(self.sessionNum) + str(self.testNum) + ".csv"
        finally:
            print("File Name :" + self.fileName)

    @pyqtSlot(int)
    def setPatientNum(self, num):
        self.patientNum = num
        print("Patient num = ", str(self.patientNum))
        self.makeFileNameSig.emit()

    @pyqtSlot(int)
    def setSessionNum(self, num):
        self.sessionNum = num
        print("Session num = ", str(self.sessionNum))
        self.makeFileNameSig.emit()

    @pyqtSlot(int)
    def setTestNum(self, num):
        self.testNum = num
        print("Test num = ", str(self.testNum))
        self.makeFileNameSig.emit()

    @pyqtSlot(str)
    def setWorkDir(self, dir_name):
        self.workDir = dir_name
        print("Dir Name :" + self.workDir)
        self.makeFileNameSig.emit()

    def startRecord(self):
        if self.workDir == None:
            raise NotADirectoryError
        elif os.path.isfile(self.fileName):
            raise FileExistsError
        else:
            self.file = open(self.fileName, 'w')
            self.writer = csv.writer(self.file, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

    @pyqtSlot(float)
    def writeValue(self, value):
        self.writer.writerow([value])

    @pyqtSlot()
    def stopRecord(self):
        self.file.close()

