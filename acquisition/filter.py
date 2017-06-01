import sys
import numpy
from collections import deque
from PyQt5.QtCore import (QObject, QThread, pyqtSignal, pyqtSlot)


class Filter (QObject):
    num_chan = 10
    dataList = []
    filtered = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.buffer = [deque(2*[0], 2) for i in range(self.num_chan)]

    @pyqtSlot(list)
    def resfilter(self, res_val):
        if len(res_val) != self.num_chan:
            return
        for i in range(len(res_val)):
            self.buffer[i].append(res_val[i])
        self.dataList = list(map(self.mean, list(self.buffer)))
        self.filtered.emit(self.dataList)

    def mean(self, array):
        return sum(array)/len(array)
