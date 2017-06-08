import sys
import os
import subprocess
import matplotlib
from acquisition.GUI import MainInterface
from PyQt5.QtCore import (pyqtSlot, QObject, QThread)
from PyQt5.QtWidgets import (QApplication)
from acquisition.server import Server
from acquisition.file_writer import FileWriter
from acquisition.filter import  Filter

matplotlib.use("Qt5Agg")

class AppManager(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.gui = MainInterface()

        self.thread = QThread()
        self.producer = Server()
        self.filter = Filter()
        self.uartProcess = None

        self.producer.moveToThread(self.thread)
        self.thread.started.connect(self.producer.process)
        self.producer.finished.connect(self.thread.quit)
        self.producer.finished.connect(self.producer.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.fileWriter = FileWriter()

        self.connectGuiEvents()

        self.producer.data_read.connect(self.filter.resfilter)
        self.filter.filtered.connect(self.gui.monitorGraph.update_queue)
        self.thread.start()


    def connectGuiEvents(self):
        self.gui.startButton.clicked.connect(self.startButtonHandle)
        self.gui.recordButton.clicked.connect(self.recordButtonHandle)
        self.gui.grphNumSampleSpinBox.valueChanged.connect(self.gui.monitorGraph.setNumSample)
        self.gui.grphScaleDoubleSpinBox.valueChanged.connect(self.gui.monitorGraph.scaleUpdate)
        self.gui.grphOffsetDoubleSpinBox.valueChanged.connect(self.gui.monitorGraph.offsetUpdate)
        self.gui.patientSpinBox.valueChanged.connect(self.fileWriter.setPatientNum)
        self.gui.sessionSpinBox.valueChanged.connect(self.fileWriter.setSessionNum)
        self.gui.testSpinBox.valueChanged.connect(self.fileWriter.setTestNum)
        self.gui.workingDirSelect.valueChanged.connect(self.fileWriter.setWorkDir)


    @pyqtSlot()
    def startButtonHandle(self):
        if self.gui.startButton.isChecked():
            self.gui.monitorGraph.clearGraph()
            self.uartProcess = subprocess.Popen(["python2", os.getcwd() + "/uart_process.py"])
            self.gui.startButton.setText("Stop")
        else:
            self.uartProcess.terminate()
            self.gui.startButton.setText("Start")
            self.gui.statusBar().showMessage('Ready')
            if self.gui.recordButton.isChecked():
                self.fileWriter.stopRecord()
                self.gui.recordButton.setChecked(False)

    @pyqtSlot()
    def recordButtonHandle(self):
        if self.gui.recordButton.isChecked():
            try:
                 self.fileWriter.startRecord()
            except NotADirectoryError:
                self.gui.statusBar().showMessage('No such Directory, Pease Chose a Working directory')
                self.gui.recordButton.setChecked(False)
            except FileExistsError:
                self.gui.statusBar().showMessage('The file already exists, please change test, session or patient number')
                self.gui.recordButton.setChecked(False)
            else:
                self.filter.filtered.connect(self.fileWriter.writeValue)
                self.gui.recordButton.clicked.connect(self.fileWriter.stopRecord)
                self.gui.statusBar().showMessage('Recording')
        else:
            self.filter.filtered.disconnect(self.fileWriter.writeValue)
            self.gui.recordButton.clicked.disconnect(self.fileWriter.stopRecord)
            self.gui.statusBar().showMessage('Ready')




"""
-----------------------------------------------------------------------------
                            Application Start
-----------------------------------------------------------------------------
"""


def main() :
    app = QApplication(sys.argv) #define a Qt application
    main_manager = AppManager(app)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()