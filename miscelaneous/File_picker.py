#!/usr/bin/env python
#
# [SNIPPET_NAME: File Picker]
# [SNIPPET_CATEGORIES: PyQt4]
# [SNIPPET_DESCRIPTION: An example file picker]
# [SNIPPET_AUTHOR: Darren Worrall <dw@darrenworrall.co.uk>]
# [SNIPPET_LICENSE: GPL]
# [SNIPPET_DOCS: http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qfiledialog.html]

# example filepicker.py

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QPushButton, QFileDialog)


class FilePicker(QWidget):
    """
    An example file picker application
    """

    def __init__(self):
        # create GUI
        QMainWindow.__init__(self)
        self.setWindowTitle('File picker')
        # Set the window dimensions
        self.resize(300, 75)

        # vertical layout for widgets
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        # Create a label which displays the path to our chosen file
        self.lbl = QLabel('No file selected')
        self.vbox.addWidget(self.lbl)

        # Create a push button labelled 'choose' and add it to our layout
        btn = QPushButton('Choose file', self)
        self.vbox.addWidget(btn)

        # Connect the clicked signal to the get_fname handler
        btn.clicked.connect(self.get_fname)

    def get_fname(self):
        """
        Handler called when 'choose file' is clicked
        """
        # When you call getOpenFileName, a file picker dialog is created
        # and if the user selects a file, it's path is returned, and if not
        # (ie, the user cancels the operation) None is returned
        fname = QFileDialog.getExistingDirectory(self, 'Select directory')
        if fname:
            self.lbl.setText(str(fname))
        else:
            self.lbl.setText('No file selected')


# If the program is run directly or passed as an argument to the python
# interpreter then create a FilePicker instance and show it
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = FilePicker()
    gui.show()
    app.exec_()
