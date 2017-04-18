import sys
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtCore import (pyqtSlot, QObject)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QDesktopWidget, QShortcut, qApp, QFormLayout,QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QSpinBox, QComboBox)
from PyQt5.QtGui import (QKeySequence)
from acquisition.prodcons import Producer
from acquisition.mygraphs import *


class AppManager(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.gui = MainInterface()
        self.producerTread = Producer()

        self.producerTread.value_read.connect(self.gui.monitorGraph.update_figure)
        self.producerTread.value_read.connect(self.gui.frequencyGraph.update_figure)
        self.producerTread.start()


"""
-----------------------------------------------------------------------------
                                GUI
-----------------------------------------------------------------------------
"""


class MainInterface (QMainWindow) :
    """Main interface of the application """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
    # Shortcuts to Quit app
        self.shortcutQ = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcutW = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcutQ.activated.connect(qApp.quit)
        self.shortcutW.activated.connect(qApp.quit)

    # Setting up size
        self.setFixedSize(1020, 600)
        self.center()
        self.setWindowTitle('HandTrack')

    # Defining Layout
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidgetLayout = QGridLayout(self.centralWidget)

    # Importing widgets to layout
        self.create_Graphs()
        self.centralWidgetLayout.addWidget(self.graphsBox, 0, 0)
        self.create_Control()
        self.centralWidgetLayout.addWidget(self.controlBox, 0, 1)
        self.centralWidget.setLayout(self.centralWidgetLayout)

    # Creating statusBar
        self.statusBar().showMessage('Ready')
        self.show()

    def center(self):
        """centering the main window"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def create_Graphs(self):
        """Creates two vertically superposed graphs"""
        self.graphsBox = QWidget()
        graphsBoxLayout = QVBoxLayout()

        self.monitorGraph = DynamicGraphCanvas()
        self.frequencyGraph = DynamicGraphCanvas()

        graphsBoxLayout.addWidget(self.monitorGraph)
        graphsBoxLayout.addWidget(self.frequencyGraph)

        self.graphsBox.setLayout(graphsBoxLayout)

    def create_Control(self):
        """Creates a control pannel"""
        self.controlBox = QWidget()
        controlBoxLayout = QVBoxLayout()

        self.startButton = QPushButton("Start")
        self.startButton.setCheckable(True)
        self.startButton.setMaximumWidth(180)
        controlBoxLayout.addWidget(self.startButton)

        self.create_simu_pilot()
        self.simuPilot.resize(100, 250)
        controlBoxLayout.addWidget(self.simuPilot)

        self.create_session_pilot()
        self.sessionPilot.resize(100, 250)
        controlBoxLayout.addWidget(self.sessionPilot)

        self.controlBox.setLayout(controlBoxLayout)

    def create_simu_pilot(self):
        """Control panel dedicated to simulation parameters"""
        self.simuPilot = QWidget()
        layout = QFormLayout()

        self.freqSpinBox = QSpinBox()
        self.freqSpinBox.setRange(0, 100)
        layout.addRow(QLabel("Sampling Frequency"), self.freqSpinBox)

        self.channelComboBox = QComboBox()
        for i in range(10):
            self.channelComboBox.addItem("%s" % str(i+1))
        layout.addRow(QLabel("Channel"), self.channelComboBox)

        self.simuPilot.setLayout(layout)

    def create_session_pilot(self):
        """Control panel dedicated to session specific informations"""
        self.sessionPilot = QWidget()
        layout = QFormLayout()

        self.patientSpinBox = QSpinBox()
        self.patientSpinBox.setRange(0, 100000)
        layout.addRow(QLabel("Patient number"), self.patientSpinBox)

        self.sessionSpinBox = QSpinBox()
        self.sessionSpinBox.setRange(0, 100000)
        layout.addRow(QLabel("Session number"), self.sessionSpinBox)

        self.testSpinBox = QSpinBox()
        self.testSpinBox.setRange(0, 100000)
        layout.addRow(QLabel("Test number"), self.testSpinBox)

        self.sessionPilot.setLayout(layout)


"""
-----------------------------------------------------------------------------
                            Application Launch
-----------------------------------------------------------------------------
"""


def main() :
    app = QApplication(sys.argv) #define a Qt application
    main_manager = AppManager(app)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()