import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import (QMainWindow,
                             QWidget, QDesktopWidget, QShortcut,
                             qApp, QFormLayout,QVBoxLayout, QGridLayout, QPushButton,
                             QLabel, QSpinBox, QComboBox,
                             QDoubleSpinBox)
from PyQt5.QtGui import (QKeySequence)
from PyQt5.QtCore import Qt
from acquisition.mygraphs import *
from acquisition.repo_select import RepoSelect
import serial.tools.list_ports

"""
-----------------------------------------------------------------------------
                                GUI
-----------------------------------------------------------------------------
"""


class MainInterface (QMainWindow) :
    """Main interface of the application """
    chanChangeSig = pyqtSignal(int)

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

    # Handle channel change event
        self.channelComboBox.currentIndexChanged.connect(self.chanChange)
        self.chanChangeSig.connect(self.monitorGraph.channelUpdate)

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
        #self.frequencyGraph = DynamicGraphCanvas()

        graphsBoxLayout.addWidget(self.monitorGraph)
        #graphsBoxLayout.addWidget(self.frequencyGraph)

        self.graphsBox.setLayout(graphsBoxLayout)

    def create_Control(self):
        """Creates a control pannel"""
        self.controlBox = QWidget()
        controlBoxLayout = QVBoxLayout()

        self.startButton = QPushButton()
        self.startButton.setText("Start")
        self.startButton.setCheckable(True)
        self.startButton.setMaximumWidth(180)
        controlBoxLayout.addWidget(self.startButton)

        self.recordButton = QPushButton()
        self.recordButton.setText("Record")
        self.recordButton.setCheckable(True)
        self.recordButton.setMaximumWidth(180)
        self.recordButton.setEnabled(False)
        controlBoxLayout.addWidget(self.recordButton)

        self.calibrateButton = QPushButton()
        self.calibrateButton.setText("Calibrate")
        self.calibrateButton.setCheckable(True)
        self.calibrateButton.setMaximumWidth(180)
        self.calibrateButton.setEnabled(False)
        controlBoxLayout.addWidget(self.calibrateButton)


        self.serialComboBox = SerialCombobox()
        self.serialComboBox.clicked.connect(self.seriral_interface_chosen)
        controlBoxLayout.addWidget(self.serialComboBox)

        self.create_simu_pilot()
        self.simuPilot.resize(100, 250)
        controlBoxLayout.addWidget(self.simuPilot)

        self.R_value_label = QLabel("R = 0.0")
        self.R_value_label.setAlignment(Qt.AlignCenter)
        controlBoxLayout.addWidget(self.R_value_label)

        self.create_session_pilot()
        self.sessionPilot.resize(100, 250)
        controlBoxLayout.addWidget(self.sessionPilot)

        self.controlBox.setLayout(controlBoxLayout)

    def create_simu_pilot(self):
        """Control panel dedicated to simulation parameters"""
        self.simuPilot = QWidget()
        layout = QFormLayout()

        # self.freqSpinBox = QSpinBox()
        # self.freqSpinBox.setRange(0, 1000)
        # self.freqSpinBox.setValue(50)
        # layout.addRow(QLabel("Frequency"), self.freqSpinBox)

        self.channelComboBox = QComboBox()
        for i in range(5):
            self.channelComboBox.addItem("%s" % str(i+1))
        layout.addRow(QLabel("Channel"), self.channelComboBox)

        self.grphScaleDoubleSpinBox = QDoubleSpinBox()
        self.grphScaleDoubleSpinBox.setRange(.1, 1000000)
        self.grphScaleDoubleSpinBox.setValue(500.0)
        layout.addRow(QLabel("Scale"), self.grphScaleDoubleSpinBox)

        self.grphOffsetDoubleSpinBox = QDoubleSpinBox()
        self.grphOffsetDoubleSpinBox.setRange(-1000000, 1000000)
        self.grphOffsetDoubleSpinBox.setValue(-1000.0)
        layout.addRow(QLabel("Offset"), self.grphOffsetDoubleSpinBox)

        self.grphNumSampleSpinBox = QSpinBox()
        self.grphNumSampleSpinBox.setRange(10, 100000)
        self.grphNumSampleSpinBox.setValue(1000)
        layout.addRow(QLabel("Num Samples"), self.grphNumSampleSpinBox)

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

        layout.addRow(QLabel())

        layout.addRow(QLabel("Working directory :"))
        self.workingDirSelect = RepoSelect()
        self.workingDirSelect.valueChanged.connect(self.dir_chosen)
        layout.addRow(self.workingDirSelect)

        self.sessionPilot.setLayout(layout)

    @pyqtSlot()
    def chanChange(self):
        self.chanChangeSig.emit(self.channelComboBox.currentIndex())

    @pyqtSlot(list)
    def updateRLabel(self, next_value):
        self.R_value_label.setText("R = {0:.2f}".format(next_value[self.channelComboBox.currentIndex()]))

    @pyqtSlot()
    def seriral_interface_chosen(self):
        self.calibrateButton.setEnabled(True)
        self.serialComboBox.clicked.disconnect(self.seriral_interface_chosen)

    @pyqtSlot()
    def dir_chosen(self):
        self.recordButton.setEnabled(True)


class SerialCombobox(QComboBox):
    clicked = pyqtSignal()

    def showPopup(self):
        self.clicked.emit()
        self.clear()
        for serial_chan in list(serial.tools.list_ports.comports()):
            self.addItem(serial_chan.device)
            super(SerialCombobox, self).showPopup()

