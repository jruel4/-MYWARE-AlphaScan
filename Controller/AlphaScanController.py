# Server code for streaming tcp connection
import socket
import time
from threading import Thread, Event
from pylsl import StreamInfo, StreamOutlet
import random
from CommandDefinitions import *

class AlphaScanDevice:
    
    def __init__(self):

        ###############################################################################
        # TCP Settings
        ###############################################################################
        self.TCP_IP = ''
        self.TCP_PORT = 50007                 #CONFIGURABLE
        self.user_input = ''
        self.data = ''
        
        ###############################################################################
        # UDP Settings
        ###############################################################################
        self.UDP_IP = "192.168.1.17"      #This gets over written dynamically
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
        self.begin = 0
        self.end = 0
        
        self.info = StreamInfo('AlphaScan', 'EEG', 8, 100, 'float32', 'myuid34234')
        self.outlet = StreamOutlet(self.info)
        self.mysample = [random.random(), random.random(), random.random(),
            random.random(), random.random(), random.random(),
            random.random(), random.random()]
            
        self.SysParams = {'vcc':None,
                          'free_heap':None,
                          'mcu_chip_id':None,
                          'sdk_ver':None,
                          'boot_ver':None,
                          'boot_mode':None,
                          'cpu_freq_mhz':None,
                          'flash_chip_id':None,
                          'flash_chip_real_size':None,
                          'flash_chip_size':None,
                          'flash_chip_speed':None,
                          'flash_chip_mode':None}
        
    def init_TCP(self):
        ###############################################################################
        # Initialize TCP Port
        ###############################################################################
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        
        self.s.bind((self.TCP_IP,self.TCP_PORT)) 
        # error: [Errno 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
        
        self.s.settimeout(2)
        self.s.listen(1)        
        try:
            self.conn,addr = self.s.accept()
            self.conn.settimeout(.05)
            time.sleep(0.01) # time for device to respond
            self.UDP_IP = addr[0]
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
                
        
    def generic_tcp_command_BYTE(self, cmd, extra = ''):
        ###############################################################################
        # Get adc status
        ###############################################################################

        self.flush_TCP()
        self.conn.send((chr(TCP_COMMAND[cmd]) + extra + chr(127)).encode('utf-8'))
        time.sleep(0.05)
        try:
            r_string = self.conn.recv(64)
        except:
            r_string = 'no_response'
        return r_string
        
    def generic_tcp_command_OPCODE(self, opcode, extra = ''):
        ###############################################################################
        # Get adc status
        ###############################################################################

        self.flush_TCP()
        self.conn.send((chr(opcode) + extra + chr(127)).encode('utf-8'))
        time.sleep(0.05)
        try:
            r_string = self.conn.recv(64)
        except:
            r_string = 'no_response'
        return r_string
        
    def generic_tcp_command_STRING(self, txt):
        ###############################################################################
        # Get adc status
        ###############################################################################

        self.flush_TCP()
        self.conn.send((txt + chr(127)).encode('utf-8'))
        time.sleep(0.05)
        try:
            r_string = self.conn.recv(64)
        except:
            r_string = 'no_response'
        return r_string
        
    def read_tcp(self, num_bytes=64):
        try:
            r_string = self.conn.recv(num_bytes)
        except:
            r_string = 'no_response'
        return r_string
    
    def sync_adc_registers(self):
        ###############################################################################
        # Get all registers and return as list of lists
        ###############################################################################
        return [[True if i % 2 == 0 else False for i in range(8)] for j in range(24)]


    def initiate_UDP_stream(self):
        ###############################################################################
        # Begin UDP adc stream
        ###############################################################################

        # Start UDP rcv thread
        self.LSL_Thread = Thread(target=self.DEV_printStream)
        self.LSL_Thread.start()
        self.DEV_streamActive.set()  
        # Send command to being 
        self.begin = time.time()
        return self.generic_tcp_command_BYTE("ADC_start_stream")
        
    def terminate_UDP_stream(self):
        ###############################################################################
        # End UDP adc stream
        ###############################################################################
        
        #TODO NEED terminatino ACK, if NACK then resend termination command        
        
        try:
            self.sock.sendto(('ttt'.encode('utf-8')), (self.UDP_IP, self.UDP_PORT))
            
        except: #Make specific to error: [Errno 9] Bad file descriptor
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192)
            self.sock.bind(('',self.UDP_PORT))
            self.sock.settimeout(0)
            self.sock.sendto(('ttt'.encode('utf-8')), (self.UDP_IP, self.UDP_PORT))
        self.end = time.time()
        self.DEV_streamActive.clear()
        time.sleep(0.01)
        self.sock.close()
        drops = self.get_drop_rate()
        avail = ((1.0 - ((drops * 1.0) / len(self.inbuf)))*100.0)
        pckt_rate = len(self.inbuf)/(self.end-self.begin)
        return "Not Streaming", str(pckt_rate),  str(avail), str(len(self.inbuf)), str(drops)
    
    
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
        self.conn.send('u'+''.join([str(t) for t in reg_to_update])+chr(127).encode('utf-8'))
        time.sleep(0.01) # Time for device to respond
        return

    def update_command_map(self):
        # create csv string from command map dict
        self.flush_TCP()
        self.conn.send((chr(TCP_COMMAND["GEN_update_cmd_map"]) + "_begin_cmd_map_" + str(TCP_COMMAND) + ',  '+chr(127)).encode('utf-8')) #NOTE: comma is necessary
        time.sleep(0.01)
        try:
            r_string = self.conn.recv(64)
        except:
            r_string = 'no_response'
        return r_string
        
    def get_drop_rate(self):
        i = 0
        drops = 0
        total_pckts = len(self.inbuf)
        if total_pckts == 0: return 
        for n in self.inbuf:
            if i != n:
                drops += 1
                i = n
            if i == 255: #wrap around
                i = 0
            else:
                i += 1
        # return success rate
        return drops
    
    def broadcast_disco_beacon(self):
        # send broadcast beacon for device to discover this host
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto('alpha_scan_beacon_xbx_'+str(self.TCP_PORT)+'_xex',('255.255.255.255',self.UDP_PORT)) #TODO this subnet might not work on all LAN's (see firmware method)
        # send desired TCP port in this beacon 
        s.close();
        
    def listen_for_device_beacon(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', self.UDP_PORT))
        s.settimeout(0.001)
        try:
            data,addr = s.recvfrom(1024)
            if "I_AM_ALPHA_SCAN" in data:
                return True
        except:
            pass
        s.close()
        return False
        
    def connect_to_device(self):
        self.broadcast_disco_beacon()
        return self.init_TCP()
        
    def set_udp_delay(self, delay):
        extra = "_b_"+str(delay)+"_e_"
        return self.generic_tcp_command_BYTE("ADC_set_udp_delay", extra)
    
    def parse_sys_commands(self):
        #read tcp buff
        buf = self.read_tcp(1024)
        #check for complete system params respons
        if ('begin_sys_commands' not in buf) or ('end_sys_commands' not in buf):
            return False
        #else begin parsing
        buf_arr = buf.split(",")
        for e in buf_arr:
            for k in self.SysParams.keys():
                if k in e:
                    self.SysParams[k] = e[e.find(":")+1:]
                    break
        return True
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    