import sys
import random
from PyQt5.QtCore import (QThread, pyqtSignal, QTimer, QObject, pyqtSlot)
from PyQt5.QtWidgets import QApplication

class Producer(QThread):
    mySignal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.mySignal.connect(handle)

    def run(self):
        while True:
            some_string = [random.randint(0, 10) for i in range(4)]
            self.mySignal.emit(some_string)

@pyqtSlot(list)
def handle(some_string):
    print(some_string)

if __name__ == "__main__":
    app = QApplication(sys.argv)  # define a Qt application
    mainThread = Producer()
    mainThread.start()
