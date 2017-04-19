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
    def __init__(self, *args, **kwargs):
        GraphCanvas.__init__(self, *args, **kwargs)
        self.figUpdate.connect(self.update_figure)

    def compute_initial_figure(self):
        self.values = deque(1000 * [0], 1000)
        self.counter = 0
        x_achse = arange(0, 1000, 1)
        y_achse = array([.0] * 1000)
        self.ax.grid(True)
        self.ax.set_title("Real time Waveform Plot")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Amplitude")
        self.ax.axis([0, 1000, -1.5, 1.5])
        #self.manager = get_current_fig_manager()
        self.line1 = self.ax.plot(x_achse, y_achse, '-')

    def connect_signal(self):
        self.figUpdate.connect(self.update_queue)


    @pyqtSlot()
    def update_figure(self):
        self.CurrentXAxis = arange(len(self.values)-1000, len(self.values), 1)  # In theory should be arrange(1, 100, 1)
        self.line1[0].set_data(self.CurrentXAxis, array(list(self.values)))
        self.ax.axis([self.CurrentXAxis.min(), self.CurrentXAxis.max(), -1.5, 1.5])
        self.fig.canvas.draw()

    @pyqtSlot(float)
    def update_queue(self, next_value):
        self.values.append(next_value)
        #  print("%s" % str(list(self.values)[-1]))
        self.counter += 1
        if self.counter >= 10:
            self.figUpdate.emit()
            self.counter = 0


