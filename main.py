from select import select
import sys
import random
from time import sleep, time
from xmlrpc.client import ProtocolError
import matplotlib
import numpy as np
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QSizePolicy,qApp,QDialog,QLabel,QAction
from PyQt5 import QtGui,QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas , NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from Ui_main import *
from socket_server import *
import threading

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(fig)
        self.axes = fig.add_subplot(111)      
        self.axes.set(facecolor='#ffffff')


class Scope(MplCanvas):
    def __init__(self, amp, amp_bias, time_length, time_bias=0 ):
        super(Scope, self).__init__()
        self.amp = amp
        self.amp_bias = amp_bias
        self.time_length = time_length
        self.time_bias = time_bias
   
        self._plot_ref = None

        self.x = np.arange(self.time_length) 
        self.y = self.amp * np.arange(self.time_length)  + self.amp_bias 
        self.axes.grid(linestyle=':', color='#000000')
        self.axes.axis([0, self.time_length, -1024, 1024])
        self.update_figure()
    
    def change_bias(self, amp_bias):
        self.amp_bias = amp_bias 

    def change_amp(self, amp):
        self.amp = amp

    def change_timescale(self, time_length):
        self.time_length = time_length
    
    def change_plot_data(self, y):
        self.x = np.arange(self.time_length)
        self.y = self.amp * (np.append(self.y, y)[1024:])  + self.amp_bias 
        size_y = len(self.y)
        if size_y > self.time_length:
            self.y = self.y[size_y-self.time_length:]
        elif size_y < self.time_length:
            np.append(  self.y, np.arange(self.time_length - size_y))


    def update_figure(self):
        # Note: we no longer need to clear the axis.
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.axes.plot(self.x, self.y, 'r')
            self._plot_ref = plot_refs[0]
        else:
            # print(self.amp)
            
            self._plot_ref.set_ydata(self.y)
            self._plot_ref.set_xdata(self.x)
            self.axes.axis([0, self.time_length, -256, 256])

        # Trigger the canvas to update and redraw.
        self.draw()

       


class Ui_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui_MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.scope = Scope(1, 0, 10000)
        self.toolbar = NavigationToolbar(self.scope, self)
        self.gridlayout = QVBoxLayout(self.groupBox)
        self.gridlayout.addWidget(self.toolbar)
        self.gridlayout.addWidget(self.scope)   

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.scope.update_figure)
        self.timer.start()
        self.udp = udp_client()

        self.dial_ch1_amp.valueChanged.connect(self.change_amp) 
        self.dial_ch1_bais.valueChanged.connect(self.change_bias)
        self.dial_time_scale.valueChanged.connect(self.change_time_scale)
        self.btn_reset.clicked.connect(self.reset_scope)
        self.net_btn.clicked.connect(self.connect_server)
        self.btn_sample.clicked.connect(self.get_adc_sample)

    def change_amp(self, amp):
        self.scope.change_amp(amp)
        self.scope.update_figure()

    def change_bias(self, bias):
        self.scope.change_bias(bias)
        self.scope.update_figure()

    def change_time_scale(self, time_scale):
        self.scope.change_timescale(time_scale)
        self.scope.update_figure()


    def reset_scope(self):
        self.scope.change_amp(1)
        self.scope.change_bias(0)
        self.scope.change_timescale(1024)
        self.scope.update_figure()

    def connect_server(self):
        # not connected
        if self.udp.server_is_connected == 0:
            # get the server address
            self.ip_addr = self.ip_editor.text()
            self.ip_port = int(self.port_editor.text())
            # create socket and connect to server
            self.udp.connect_to_server((self.ip_addr, self.ip_port))
            # change the botton text
            self.net_btn.setText("disconnect")
        
        # already connected to server
        elif self.udp.server_is_connected == 1:
            # disconnect from server
            self.udp.disconnect_from_server()
            # change the botton text
            self.net_btn.setText("connect")
    
    def closeEvent(self, QCloseEvent ):
        # in case of quit withoput close socket
        if self.udp.server_is_connected == 1:
            self.udp.disconnect_from_server()
        QCloseEvent.accept()

    def get_adc_sample(self):
        if self.udp.server_is_connected == 1:
            ret_data = self.udp.udp_get_sample((self.ip_addr, self.ip_port))
            self.scope.change_plot_data(ret_data)
            self.scope.update_figure()



if __name__ == "__main__":
    # create an application
    app =  QApplication(sys.argv)
    # initialize the window
    myWin = Ui_MainWindow()
    # display the window
    myWin.show()
    # exit the program
    sys.exit(app.exec_())
