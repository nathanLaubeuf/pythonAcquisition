import sys
import time
from random import random
from PyQt5.QtCore import (QObject, QThread, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QApplication)


class Producer(QObject):
    """
    Producer thread
    This thread will receive data from the board and emit a signal when new data is available
    """
    value_read = pyqtSignal(float)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()

    @pyqtSlot()
    def process(self):
        while True:
            next_value = -1.0 + random()*2
            self.value_read.emit(next_value)
            time.sleep(0.001)

@pyqtSlot(float)
def handle(next_value):
    """Test handler"""
    print("%s" % str(next_value))

if __name__ == "__main__":
    app = QApplication(sys.argv)  # define a Qt application

    thread = QThread()
    producer = Producer()

    producer.moveToThread(thread)
    thread.started.connect(producer.process)
    producer.finished.connect(thread.quit)
    producer.finished.connect(producer.deleteLater)
    thread.finished.connect(thread.deleteLater)

    producer.value_read.connect(handle)

    thread.start()

    sys.exit(app.exec_())
