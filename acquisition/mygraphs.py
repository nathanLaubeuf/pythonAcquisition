from collections import deque
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pylab import (figure, arange, array, get_current_fig_manager, show)
from PyQt5.QtCore import pyqtSlot
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

    def compute_initial_figure(self):
        """To be overridden"""
        pass


class DynamicGraphCanvas(GraphCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        GraphCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.values = deque(100*[0], 100)
        x_achse = arange(0, 100, 1)
        y_achse = array([.0] * 100)
        self.ax.grid(True)
        self.ax.set_title("Real time Waveform Plot")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Amplitude")
        self.ax.axis([0, 100, -1.5, 1.5])
        #self.manager = get_current_fig_manager()
        self.line1 = self.ax.plot(x_achse, y_achse, '-')


    @pyqtSlot(float)
    def update_figure(self, next_value):
        self.values.append(next_value)
        #  print("%s" % str(list(self.values)[-1]))
        self.CurrentXAxis = arange(len(self.values)-100, len(self.values), 1)  # In theory should be arrange(1, 100, 1)
        self.line1[0].set_data(self.CurrentXAxis, array(list(self.values)))
        self.ax.axis([self.CurrentXAxis.min(), self.CurrentXAxis.max(), -1.5, 1.5])
        self.fig.canvas.draw()

