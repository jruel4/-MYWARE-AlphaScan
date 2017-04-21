

from PySide.QtCore import *
from PySide.QtGui import *
from pylsl import  StreamInlet, resolve_stream, StreamInfo, StreamOutlet
from collections import deque
from threading import Thread
import numpy as np
#from stats import rms

def rms(d): return np.sqrt(np.mean((d-np.mean(d))**2))
    
class STATS_TAB(QWidget):
    '''
    The question is, which stream do I want to grab statistics from? Well 
    for starters we can assume that a) the LSL stream is a time series and that 
    b) it will only be feeding us 1 sample at a time at 250sps. therefor we 
    probably want to implement a buffer local to the statistic module that samples 
    the desired stream and calculates statistics on that time series on demand
    '''
    
    SIG_reserve_tcp_buffer = Signal()
    
    # Define Init Method
    def __init__(self, Device, Debug):
        super(STATS_TAB, self).__init__(None)
        
        #######################################################################
        # Basic Init ##########################################################
        #######################################################################
        
        self._Device = Device
        self._Debug = Debug
        
        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout) # Does it matter when I do this?
        
        self.stat_labels = ['rms', 'min', 'max', 'avg', 'std']
        
        # Set layout formatting
        self.layout.setAlignment(Qt.AlignTop)
        #TODO self.layout.setColumnStretch(3,1)
        
        #######################################################################
        # Display system parameters
        #######################################################################
        
        self.stat_val_dict = {}
        for idx,s in enumerate(self.stat_labels):
            self.stat_val_dict[s] = QLabel("")
            self.layout.addWidget(QLabel(s.upper()+": "), idx+1, 0)
            self.layout.addWidget(self.stat_val_dict[s], idx+1, 1)
 
        # Stream selection
        self.Options_StreamSelect = QComboBox()
        self.Options_StreamSelect.insertItem(0, "Select LSL Stream")
        self.Options_StreamSelect.insertItems(1, self.get_stream_names())
        self.Options_StreamSelect.currentIndexChanged.connect(self.stream_changed)
        self.layout.addWidget(self.Options_StreamSelect, 0,0)
        
        # chan selection
        self.Options_ChanSelect = QComboBox()
        self.Options_ChanSelect.insertItem(0, "Select Channel")
        self.Options_ChanSelect.insertItems(1, [str(i+1) for i in range(8)])
        self.layout.addWidget(self.Options_ChanSelect, 0,2)
        
        
        #######################################################################
        # Add control buttons
        #######################################################################
        
        self.Button_RefreshDisplay = QPushButton("Refresh Displayed Parameters")
        self.layout.addWidget(self.Button_RefreshDisplay, 0, 1)
        self.Button_RefreshDisplay.clicked.connect(self.refresh_display)
        
        # Stream control variables
        self.selected_stream = None
        self.buf = deque(maxlen=(250*10))
    
    @Slot()
    def refresh_display(self):
        if True:
            self.stat_val_dict['rms'].setText(str(rms(self.buf)))
            self.stat_val_dict['min'].setText(str(np.min(self.buf)))
            self.stat_val_dict['max'].setText(str(np.max(self.buf)))
            self.stat_val_dict['avg'].setText(str(np.mean(self.buf)))
            self.stat_val_dict['std'].setText(str(np.std(self.buf)))
        else:
            msg = QMessageBox()
            msg.setText("Did not find complete response in buffer")
            msg.exec_()
        
    @Slot()
    def stream_changed(self, idx):
        self._Debug.append("Stream set: "+str(idx))
        self.selected_stream = idx-1

        # Setup stream and launch collection thread w/ qTimer     
        self.inlet = StreamInlet(self.streams[int(self.selected_stream)])  
        _thread = Thread(target=self.acquisition_thread)
        _thread.start()
        
        
    def get_step_size(self, gain=24.0):
        return 5.0/2**24/gain
        
    def get_stream_names(self):
        self.streams = resolve_stream('type', 'EEG')
        return [s.name() for s in self.streams]
        
    def acquisition_thread(self):
        step = self.get_step_size()
        while(True):
            data,_ = self.inlet.pull_sample()
            self.buf.append(data[self.Options_ChanSelect.currentIndex()-1]*step)




















