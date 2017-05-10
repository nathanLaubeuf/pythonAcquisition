from collections import deque
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pylab import (figure, arange, array)
from PyQt5.QtCore import (pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QSizePolicy)

"""
-----------------------------------------------------------------------------
                                Graphs
-----------------------------------------------------------------------------
"""


class GraphCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=6, height=3, dpi=120):
        self.fig = figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.MinimumExpanding,
                QSizePolicy.MinimumExpanding)
        FigureCanvas.updateGeometry(self)

    @pyqtSlot()
    def update_figure(self):
        pass


class DynamicGraphCanvas(GraphCanvas):
    """A canvas that updates itself every second with a new plot."""
    figUpdate = pyqtSignal()
    minMaxUpdateSig = pyqtSignal()
    numSample = 1000
    maxValue = 2000.0
    minValue = -2000.0
    scale = 2000.0
    offset = 0
    chanIndex = 0
    numChan = 5
    channelValues = [deque(10000 * [0], 10000) for i in range(5)]

    def __init__(self, *args, **kwargs):
        GraphCanvas.__init__(self, *args, **kwargs)
        self.figUpdate.connect(self.update_figure)
        self.minMaxUpdateSig.connect(self.minMaxUpdate)

    def compute_initial_figure(self):
        #self.values = deque(10000 * [0], 10000)
        self.counter = 0
        x_achse = arange(0, self.numSample, 1)
        y_achse = array([.0] * self.numSample)
        self.ax.grid(True)
        self.ax.set_title("Real time Waveform Plot")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Amplitude")
        self.ax.axis([0, self.numSample, self.minValue, self.maxValue])
        #self.manager = get_current_fig_manager()
        self.line1 = self.ax.plot(x_achse, y_achse, '-')

    def connect_signal(self):
        self.figUpdate.connect(self.update_queue)


    @pyqtSlot()
    def update_figure(self):
        """Updates the graph"""
        self.CurrentXAxis = arange(0, self.numSample, 1)
        self.line1[0].set_data(self.CurrentXAxis, array(list(self.channelValues[self.chanIndex])[-self.numSample:]))
        self.ax.axis([self.CurrentXAxis.min(), self.CurrentXAxis.max(), self.minValue, self.maxValue])
        self.fig.canvas.draw()

    @pyqtSlot(list)
    def update_queue(self, next_value):
        """Updates the queue and emmit a signal every 10 values to display the new values"""
        #self.values.append(next_value[self.chanIndex])
        if len(next_value) != self.numChan:
            return
        for i in range(len(self.channelValues)):
            self.channelValues[i].append(next_value[i])

        #  print("%s" % str(list(self.values)[-1]))
        self.counter += 1
        if self.counter >= 10:
            self.figUpdate.emit()
            self.counter = 0

    @pyqtSlot(int)
    def setNumSample(self, new_num_sample):
        self.numSample = new_num_sample
        self.figUpdate.emit()

    @pyqtSlot(float)
    def scaleUpdate(self, new_scale):
        self.scale = new_scale
        self.minMaxUpdateSig.emit()

    @pyqtSlot(float)
    def offsetUpdate(self, new_offset):
        self.offset = new_offset
        self.minMaxUpdateSig.emit()

    @pyqtSlot()
    def minMaxUpdate(self):
        self.minValue = - self.offset - self.scale
        self.maxValue = - self.offset + self.scale

    @pyqtSlot(int)
    def channelUpdate(self, chan):
        self.chanIndex = chan

    @pyqtSlot()
    def clearGraph(self):
        self.channelValues = [deque(10000 * [0], 10000) for i in range(self.numChan)]
