import sys
import time
import random
from PyQt5.QtCore import (QThread, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import QApplication

class Producer(QThread):
    mySignal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            l = [random.randint(0, 10) for i in range(4)]
            self.mySignal.emit(l)
            time.sleep(0.125)


@pyqtSlot(list)
def handle(some_string):
    print(some_string)

if __name__ == "__main__":
    app = QApplication(sys.argv)  # define a Qt application
    mainThread = Producer()
    mainThread.run()
