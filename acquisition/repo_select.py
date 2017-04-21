import sys
from PyQt5.QtCore import (pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QPushButton, QLineEdit, QFileDialog)


class RepoSelect(QWidget):
    """
    Working directory selector class
    emits a signal with the new folder name each time the folder is changed
    """
    valueChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.dirName = ""
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.folderNameLine = QLineEdit()
        self.folderNameLine.setReadOnly(True)
        self.selectFolderBtn = QPushButton("Select")
        self.selectFolderBtn.setMaximumWidth(80)

        self.selectFolderBtn.clicked.connect(self.dirHandler)

        layout.addWidget(self.folderNameLine)
        layout.addWidget(self.selectFolderBtn)
        self.setLayout(layout)

    @pyqtSlot()
    def dirHandler(self):
        self.repoName = QFileDialog.getExistingDirectory(self, 'Select directory')
        self.folderNameLine.setText(self.repoName)
        self.valueChanged.emit(self.repoName)

if __name__ == "__main__":
    app = QApplication(sys.argv) #define a Qt application
    ui = RepoSelect()
    ui.show()
    sys.exit(app.exec_())
