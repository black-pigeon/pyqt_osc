from multiprocessing import set_forkserver_preload
from re import S
import sys
import random
from time import sleep, time
import matplotlib
import numpy as np
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QSizePolicy,qApp,QDialog,QLabel,QAction
#import win32ui
#import win32api
from PyQt5 import QtGui,QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas , NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from Ui_main import *

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(fig)
        self.axes = fig.add_subplot(111)      
        self.axes.set(facecolor='#ffffff')


class Scope(MplCanvas):
    def __init__(self, amp, bias, time_length):
        super(Scope, self).__init__()
        self.amp = amp
        self.bias = bias
        self.time_length = time_length

        self._plot_ref = None

        self.Fs = 10e6 # sample rate 1M
        self.dt = 1/self.Fs
        self.freq = 50000
        self.x = np.arange(time_length) * self.dt
        self.y = self.amp * np.sin(2 * np.pi * self.freq * self.x) + self.bias 
        self.axes.grid(linestyle=':', color='#000000')
        self.axes.axis([0, time_length* self.dt, -10, 10])
        self.update_figure()
    
    def change_bias(self, bias):
        self.bias = bias

    def change_amp(self, amp):
        self.amp = amp

    def change_timescale(self, time_length):
        self.time_length =time_length
        self.x = np.arange(self.time_length) * self.dt
        
    def update_figure(self):
        
        # Note: we no longer need to clear the axis.
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.axes.plot(self.x, self.y, 'r')
            self._plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref.set_ydata(self.y)
            self._plot_ref.set_xdata(self.x)
            self.axes.axis([0, self.time_length* self.dt, -10, 10])

        # Trigger the canvas to update and redraw.
        self.draw()

       


class Ui_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui_MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.scope = Scope(2, 1, 1000)
        self.toolbar = NavigationToolbar(self.scope, self)
        self.gridlayout = QVBoxLayout(self.groupBox)
        self.gridlayout.addWidget(self.toolbar)
        self.gridlayout.addWidget(self.scope)   

        self.timer = QtCore.QTimer()
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.scope.update_figure)
        self.timer.start()   




if __name__ == "__main__":
    # create an application
    app =  QApplication(sys.argv)
    # initialize the window
    myWin = Ui_MainWindow()
    # display the window
    myWin.show()
    # exit the program
    sys.exit(app.exec_())
