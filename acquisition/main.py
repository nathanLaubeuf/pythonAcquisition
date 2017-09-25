import sys
import os
import subprocess
import matplotlib
from acquisition.GUI import MainInterface
from PyQt5.QtCore import (pyqtSlot, QObject, QThread)
from PyQt5.QtWidgets import (QApplication)
from acquisition.server import Server
from acquisition.file_writer import FileWriter
from acquisition.calibration import ExCaliber
from acquisition.filter import Filter

matplotlib.use("Qt5Agg")

class AppManager(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.gui = MainInterface()

        self.thread = QThread()
        self.server = Server()
        self.filter = Filter()

        self.uartProcess = None

        self.server.moveToThread(self.thread)
        self.thread.started.connect(self.server.process)
        self.server.finished.connect(self.thread.quit)
        self.server.finished.connect(self.server.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.fileWriter = FileWriter()

        self.calibrator = ExCaliber()
        self.calibrator.calib_stopped.connect(self.no_serial_handle)
        self.calibrator.new_angle.connect(self.gui.updateALabel)

        self.connectGuiEvents()

        self.server.data_read.connect(self.filter.resfilter)
        """
        The processed values are accessible by connecting to the filtered.connect signal
        """
        self.filter.filtered.connect(self.gui.monitorGraph.update_queue)
        self.filter.filtered.connect(self.gui.updateRLabel)
        self.thread.start()


    def connectGuiEvents(self):
        """ Connect GUI events to back end """
        self.gui.startButton.clicked.connect(self.startButtonHandle)
        self.gui.recordButton.clicked.connect(self.recordButtonHandle)
        self.gui.calibrateButton.clicked.connect(self.calibrateButtonHandle)
        self.gui.grphNumSampleSpinBox.valueChanged.connect(self.gui.monitorGraph.setNumSample)
        self.gui.grphScaleDoubleSpinBox.valueChanged.connect(self.gui.monitorGraph.scaleUpdate)
        self.gui.grphOffsetDoubleSpinBox.valueChanged.connect(self.gui.monitorGraph.offsetUpdate)
        self.gui.patientSpinBox.valueChanged.connect(self.fileWriter.setPatientNum)
        self.gui.sessionSpinBox.valueChanged.connect(self.fileWriter.setSessionNum)
        self.gui.testSpinBox.valueChanged.connect(self.fileWriter.setTestNum)
        self.gui.workingDirSelect.valueChanged.connect(self.fileWriter.setWorkDir)
        self.gui.chanChangeSig.connect(self.calibrator.channel_change)
        self.gui.serialComboBox.activated[str].connect(self.calibrator.set_calib_serial)



    @pyqtSlot()
    def startButtonHandle(self):
        if self.gui.startButton.isChecked():
            self.gui.monitorGraph.clearGraph()
            self.uartProcess = subprocess.Popen(["python2.7", os.path.abspath(os.path.dirname(__file__)) + "/uart_process.py"])
            self.gui.startButton.setText("Stop")
        else:
            self.uartProcess.terminate()
            self.gui.startButton.setText("Start")
            self.gui.statusBar().showMessage('Ready')
            if self.gui.recordButton.isChecked():
                self.fileWriter.stopRecord()
                self.filter.filtered.disconnect(self.fileWriter.writeValue)
                self.gui.recordButton.clicked.disconnect(self.fileWriter.stopRecord)
                self.gui.recordButton.setChecked(False)
            if self.gui.calibrateButton.isChecked():
                self.calibrator.stop_calib()
                self.filter.filtered.disconnect(self.calibrator.stretch_res_handle)
                self.gui.calibrateButton.setChecked(False)

    @pyqtSlot()
    def calibrateButtonHandle(self):
        if self.gui.calibrateButton.isChecked():
            if self.gui.startButton.isChecked():
                self.calibrator.start_calib()
                self.filter.filtered.connect(self.calibrator.stretch_res_handle)
                self.gui.channelComboBox.setEnabled(False)
            else:
                self.gui.calibrateButton.setChecked(False)
        else:
            self.calibrator.stop_calib()
            self.gui.channelComboBox.setEnabled(True)
            self.filter.filtered.disconnect(self.calibrator.stretch_res_handle)
            self.gui.A_value_label.setText('Angle = -')

    @pyqtSlot()
    def no_serial_handle(self):
        self.gui.channelComboBox.setEnabled(True)
        self.gui.calibrateButton.setEnabled(False)
        try:
            self.filter.filtered.disconnect(self.calibrator.stretch_res_handle)
        except:
            print('Serial disconnected normally')
        self.gui.calibrateButton.setChecked(False)
        self.gui.serialComboBox.addItem('')
        self.gui.serialComboBox.setCurrentIndex(-1)
        self.gui.A_value_label.setText('Angle = -')

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