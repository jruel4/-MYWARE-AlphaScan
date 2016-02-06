# Server code for streaming tcp connection
import socket
import time
from threading import Thread, Event
from pylsl import StreamInfo, StreamOutlet
import random

class AlphaScanDevice:
    
    def __init__(self):

        ###############################################################################
        # TCP Settings
        ###############################################################################
        self.TCP_IP = ''
        self.PORT = 50007                 #CONFIGURABLE
        self.user_input = ''
        self.data = ''
        
        ###############################################################################
        # UDP Settings
        ###############################################################################
        self.UDP_IP = "192.168.1.14"      #CONFIGURABLE #TODO get this automatically from TCP conn
        self.UDP_PORT = 2390              #CONFIGURABLE
        
        self.num = 10
        self.MESSAGE = chr(self.num)
        self.num_iter = self.num * 100
        self.errors = 0
        self.reads = 0
        self.DEV_streamActive = Event()
        self.DEV_streamActive.clear()
        self.DEV_log = list()
        self.inbuf = list()  
        self.unknown_stream_errors = 0
        
        self.info = StreamInfo('AlphaScan', 'EEG', 8, 100, 'float32', 'myuid34234')
        self.outlet = StreamOutlet(self.info)
        self.mysample = [random.random(), random.random(), random.random(),
            random.random(), random.random(), random.random(),
            random.random(), random.random()]
        
    def init_TCP(self):
        ###############################################################################
        # Initialize TCP Port
        ###############################################################################
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        
        self.s.bind((self.TCP_IP,self.PORT)) #TODO Deal with previously opened connection without device reset...
        #error: [Errno 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
        
        self.s.settimeout(2)
        self.s.listen(1)        
        try:
            self.conn,addr = self.s.accept()
            self.conn.settimeout(.05)
            time.sleep(0.01) # time for device to respond
            return True
        except:
            return False
            
    def close_TCP(self):
        ################################################################################
        # Close TCP connection
        ################################################################################
        try:
            self.conn.close() #conn might not exist yet
            self.s.close()
        except:
            pass        
        
    def close_UDP(self):
        ################################################################################
        # Close UDP connection
        ################################################################################
        try:
            self.sock.close() 
        except:
            pass
    
    def DEV_printStream(self):
        ###############################################################################
        # UDP Stream thread target
        ###############################################################################
        # TODO maybe open LSL stream here
        self.errors = 0
        self.reads = 0
        self.unknown_stream_errors = 0
        self.inbuf = list()
        self.DEV_streamActive.set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',self.UDP_PORT))
        self.sock.settimeout(0)
        while self.DEV_streamActive.is_set():
            try:
                self.data = self.sock.recv(128)
                self.inbuf += [ord(self.data[23:])]
                # send to lsl stream
                
                self.outlet.push_sample(self.mysample)
                
                self.reads += 1
            except socket.error as e:
                if e.errno == 10035:
                    self.errors += 1
                elif e.errno == 9:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.sock.bind(('',self.UDP_PORT))
                    self.sock.settimeout(0)
            except:
                self.unknown_stream_errors += 1
                
                
                
                
    def get_accel_status(self):
        ###############################################################################
        # UDP Stream thread target
        ###############################################################################
        self.flush_TCP()
        self.conn.send('a\r'.encode('utf-8'))
        time.sleep(0.01) # Time for device to respond
        return self.conn.recv(64) # TODO add response validation here
        
    def get_power_status(self):
        ###############################################################################
        # UDP Stream thread target
        ###############################################################################
        self.flush_TCP()
        self.conn.send('p\r'.encode('utf-8'))
        time.sleep(0.01)
        return self.conn.recv(64)
        
    def get_adc_status(self):
        ###############################################################################
        # Get adc status
        ###############################################################################
        self.flush_TCP()
        self.conn.send('i\r'.encode('utf-8'))
        time.sleep(0.01)
        try:
            r_string = self.conn.recv(64)
        except:
            r_string = 'failed'
        return r_string
        
    def generic_tcp_command(self, cmd):
        ###############################################################################
        # Get adc status
        ###############################################################################
        # TODO use dict with unique values for commands
        self.flush_TCP()
        self.conn.send((cmd + '\r').encode('utf-8'))
        time.sleep(0.01)
        try:
            r_string = self.conn.recv(64)
        except:
            r_string = 'failed'
        return r_string
        
    def sync_adc_registers(self):
        ###############################################################################
        # Get all registers and return as list of lists
        ###############################################################################
        return [[True if i % 2 == 0 else False for i in range(8)] for j in range(24)]
        # TODO replace test code above with command to Firmware

    def initiate_UDP_stream(self):
        ###############################################################################
        # Begin UDP adc stream
        ###############################################################################
        self.LSL_Thread = Thread(target=self.DEV_printStream)
        self.LSL_Thread.start()
        self.DEV_streamActive.set()       
        self.conn.send('s\r'.encode('utf-8'))
        return "Streaming Now" # TODO need ACK validation
        
    def terminate_UDP_stream(self):
        ###############################################################################
        # End UDP adc stream
        ###############################################################################
        try:
            self.sock.sendto(('ttt'.encode('utf-8')), (self.UDP_IP, self.UDP_PORT))
        except: #Make specifi to bad file descriptor
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192)
            self.sock.bind(('',self.UDP_PORT))
            self.sock.settimeout(0)
            self.sock.sendto(('ttt'.encode('utf-8')), (self.UDP_IP, self.UDP_PORT))
            
        self.DEV_streamActive.clear()
        time.sleep(0.01)
        self.sock.close()
        return "Not Streaming, Inbuf size: "+str(len(self.inbuf)) # TODO need ACK validation
    
    
    def flush_TCP(self):
        ###############################################################################
        # Clear TCP input buffer
        ###############################################################################
        try:
            self.conn.recv(self.conn.getsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF))
        except:
            pass
    
    def flush_UDP(self):
        ###############################################################################
        # Clear udp input buffer
        ###############################################################################
        try:
            self.sock.recv(65535)
        except:
            pass
    
    def update_adc_registers(self,reg_to_update):
        #send adc registers to update over tcp
        self.flush_TCP()
        self.conn.send('u'+''.join([str(t) for t in reg_to_update])+'\r'.encode('utf-8'))
        time.sleep(0.01) # Time for device to respond
        return #TODO add validation

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    