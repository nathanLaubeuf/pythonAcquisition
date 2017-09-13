import sys
import numpy
import time
from collections import deque
from PyQt5.QtCore import (QObject, QThread, pyqtSignal, pyqtSlot)

# --  Benchmarking -- #
current_milli_time = lambda: int(round(time.time() * 1000))
# ------------------  #


class Filter (QObject):
    num_chan = 5
    dataList = []
    filtered = pyqtSignal(list)

    # --  Benchmarking -- #
    # prev_time = cur_time = 0
    # ------------------  #

    def __init__(self):
        super().__init__()
        self.buffer = [deque(2*[0], 2) for i in range(self.num_chan)]

    @pyqtSlot(list)
    def resfilter(self, res_val):
        if len(res_val) != self.num_chan:
            print("Wrong number of channels : received {0}, expected {1}".format(len(res_val), self.num_chan))
            return
        for i in range(len(res_val)):
            self.buffer[i].append(res_val[i])
        self.dataList = list(map(self.mean, list(self.buffer)))
        self.filtered.emit(self.dataList)

        # --  Benchmarking -- #
        # self.cur_time = current_milli_time()
        # print(self.cur_time - self.prev_time)
        # self.prev_time = self.cur_time
        # ------------------  #

    def mean(self, array):
        return sum(array)/len(array)
