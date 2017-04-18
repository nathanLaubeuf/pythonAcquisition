from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pylab import figure
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QSizePolicy)

"""
-----------------------------------------------------------------------------
                                Graphs
-----------------------------------------------------------------------------
"""

class GraphCanvas(FigureCanvas) :
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=6, height=3, dpi=120):
        fig = figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
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
        self.axes.clear()
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    @pyqtSlot(list)
    def update_figure(self, list):
        self.axes.clear()
        self.axes.plot([0, 1, 2, 3], list, 'r')
        self.draw()

