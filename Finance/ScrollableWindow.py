import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets,QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import pdb

class ScrollableWindow(QtWidgets.QMainWindow):
    def __init__(self, fig, callback, file):
        self.qapp = QtWidgets.QApplication([])

        QtWidgets.QMainWindow.__init__(self)
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setSpacing(0)

        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtWidgets.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)

        self.show()
        self.callback = callback
        self.file = file
        self.timer = QtCore.QTimer()
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        
        exit(self.qapp.exec_())

    def update_plot(self):
        
##        # Drop off the first y element, append a new one.
##        self.ydata = self.ydata[1:] + [random.randint(0, 10)]
#        self.canvas.axes.cla()  # Clear the canvas.
##        self.canvas.axes.plot(self.xdata, self.ydata, 'r')
##        # Trigger the canvas to update and redraw.
        self.callback(self.file)
        self.canvas.draw()
       

### create a figure and some subplots
##fig, axes = plt.subplots(ncols=3, nrows=3)
##for ax in axes.flatten():
##    ax.plot([2,3,5,1])
##
### pass the figure to the custom window
##a = ScrollableWindow(fig)
