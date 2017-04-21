import sys
import matplotlib
matplotlib.use("Qt5Agg")
from acquisition.GUI import MainInterface
from PyQt5.QtCore import (pyqtSlot, QObject, QThread)
from PyQt5.QtWidgets import (QApplication)
from acquisition.prodcons import Producer
from acquisition.file_writer import FileWritter


class AppManager(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.gui = MainInterface()

        self.thread = QThread()
        self.producer = Producer()

        self.producer.moveToThread(self.thread)
        self.thread.started.connect(self.producer.process)
        self.producer.finished.connect(self.thread.quit)
        self.producer.finished.connect(self.producer.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.fileWriter = FileWritter()

        self.connectGuiEvents()

        self.producer.value_read.connect(self.gui.monitorGraph.update_queue)
        self.thread.start()


    def connectGuiEvents(self):
        self.gui.startButton.clicked.connect(self.startButtonHandle)
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
            self.gui.startButton.setText("Stop")
            try:
                 self.fileWriter.startRecord()
            except NotADirectoryError:
                self.gui.statusBar().showMessage('No such Directory, Pease Chose a Working directory')
                self.gui.startButton.setChecked(False)
                self.gui.startButton.setText("Start")
            except FileExistsError:
                self.gui.statusBar().showMessage('The file already exists, please change test, session or patient number')
                self.gui.startButton.setChecked(False)
                self.gui.startButton.setText("Start")
            else:
                self.producer.value_read.connect(self.fileWriter.writeValue)
                self.gui.startButton.clicked.connect(self.fileWriter.stopRecord)
                self.gui.statusBar().showMessage('Recording')
        else:
            self.producer.value_read.disconnect(self.fileWriter.writeValue)
            self.gui.startButton.clicked.disconnect(self.fileWriter.stopRecord)
            self.gui.startButton.setText("Start")
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