import sys
import time
from random import random
from PyQt5.QtCore import (QThread, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import QApplication


class Producer(QThread):
    """
    Producer thread
    This thread will receive data from the board and emit a signal when new data is available
    """
    value_read = pyqtSignal(float)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            next_value = -1.5 + random()*3
            self.value_read.emit(next_value)
            time.sleep(0.05)


@pyqtSlot(float)
def handle(next_value):
    """Test handler"""
    print("%s" % str(next_value))

if __name__ == "__main__":
    app = QApplication(sys.argv)  # define a Qt application
    mainThread = Producer()
    mainThread.value_read.connect(handle)
    mainThread.run()
    sys.exit(app.exec_())
