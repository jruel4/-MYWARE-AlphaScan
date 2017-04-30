# Server code for streaming tcp connection
import socket
import time
from threading import Thread, Event
from pylsl import StreamInfo, StreamOutlet
import random
from CommandDefinitions import *
from BitPacking import twos_comp
import select

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
        self.skips = 0
        self.reads = 0
        self.DEV_streamActive = Event()
        self.DEV_streamActive.clear()
        self.DEV_log = list()
        self.inbuf = list()  
        self.unknown_stream_errors = 0
        self.begin = 0
        self.end = 0
        self.IS_CONNECTED = False
        self.time_alpha = 0
        self.time_beta = 0
        self.time_intervals = list()
        self.time_interval_count = 0
        
        self.sqwave = list()
        
        
        self.info = StreamInfo('AlphaScan', 'EEG', 8, 100, 'float32', 'uid_18')
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
                          'flash_chip_mode':None,
                          'free_sketch_space':None}
        # Debug port variables
        self.debug_port_open = False
        self.debug_port_no = 2391
        #self.open_debug_port()
        
        
    def open_debug_port(self):
        try:
            self.debug_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.debug_sock.bind(('',self.debug_port_no))
            self.debug_sock.settimeout(0)
            self.debug_port_open = True
            return True
        except:
            return False
    
    def close_debug_port(self):
        try:
            self.debug_sock.close()
            self.debug_port_open = False
            return True
        except:
            return False
    
    def read_debug_port(self):
        if not self.debug_port_open: return False
        try:
            r = self.debug_sock.recv(1024)
            if len(r) > 0:
                return r
        except:
            return False
        
    def init_TCP(self):
        ###############################################################################
        # Initialize TCP Port
        ###############################################################################
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.TCP_IP,self.TCP_PORT)) 
        # error: [Errno 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
        
        self.s.settimeout(10)
        self.s.listen(1)        
        try:
            self.conn,addr = self.s.accept()
            self.conn.settimeout(.05) # TODO maybe want to make this smaller
            time.sleep(0.01) # time for device to respond
            self.UDP_IP = addr[0] # TODO this should say TCP_IP
            self.IS_CONNECTED = True
            return True
        except:
            self.IS_CONNECTED = False
            self.close_TCP(); # cleanup socket
            return False
            
    def close_TCP(self):
        ################################################################################
        # Close TCP connection
        ################################################################################
        try:
            self.conn.close() #conn might not exist yet
            self.s.close()
            self.IS_CONNECTED = False
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
        global sqwave
        ###############################################################################
        # UDP Stream thread target
        ###############################################################################

        self.skips = 0
        self.reads = 0
        self.unknown_stream_errors = 0
        self.time_interval_count = 0
        self.inbuf = list()
        self.time_intervals = list()
        self.DEV_streamActive.set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',self.UDP_PORT))
        self.sock.settimeout(0)
        while self.DEV_streamActive.is_set():
            try:
                self.data = self.sock.recv(128)
                self.inbuf += [ord(self.data[27:])] 
                self.sqwave += [self.data]
                self.outlet.push_sample(self.mysample)
                self.reads += 1
                
                #TODO count interval
                self.count_time_interval()
                
            except socket.error as e:
                if e.errno == 10035:
                    self.skips += 1
                elif e.errno == 9:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.sock.bind(('',self.UDP_PORT))
                    self.sock.settimeout(0)
            except:
                self.unknown_stream_errors += 1
                
    def DEV_printTCPStream_OLD(self):
        global sqwave
        ###############################################################################
        # UDP Stream thread target
        ###############################################################################

        self.reads = 0
        self.unknown_stream_errors = 0
        self.time_interval_count = 0
        self.rx_count = 0
        self.pre_rx = 0
        self.timeout_count = 0
        self.test_inbuf = list()
        self.inbuf = list()
        self.time_intervals = list()
        self.DEV_streamActive.set()
        self.error_array = list()
        
        deviceData = [0 for i in range(8)]
        
        # clear tcp inbuf
        #self.conn.recv(2048) # this is not a proper flush, rx size should be set to match
        self.flush_TCP()
        
        diff = 3
        
        while self.DEV_streamActive.is_set():
            try:
                self.pre_rx += 1
                # TODO Receive and unpack sample from TCP connection
                ready = select.select([self.conn], [], [] , 0)
                if (ready[0]):
                    self.data = self.conn.recv(24+diff)
        
                    self.test_inbuf += [self.data]
                    self.rx_count += 1                
                    
                    #self.inbuf += [ord(self.data)] # #TODO this is suspect since ord should only take 1 character, and will fill quick
                    
                    # Populate fresh channel data into self.mysample
                    for j in xrange(8):
                        deviceData[j] = [self.data[diff+(j*3):diff+(j*3+3)]] 
                        val = 0
                        for i in range(3):
                            n = deviceData[j][0][i]
                            try:
                                val ^= ord(n) << ((2-i)*8)
                            except ValueError as e:
                                print("value error",e)
                            except TypeError as e:
                                print("value error",e)
                        val = twos_comp(val)
                        self.mysample[j] = val
                    
                    self.sqwave += [self.data]
                    self.outlet.push_sample(self.mysample)
                    self.reads += 1
                    
                    #TODO count interval
                    self.count_time_interval()
                
            except socket.timeout:
                self.timeout_count += 1
                
    def DEV_printTCPStream(self):
        global sqwave
        ###############################################################################
        # UDP Stream thread target
        ###############################################################################

        self.reads = 0
        self.unknown_stream_errors = 0
        self.time_interval_count = 0
        self.rx_count = 0
        self.pre_rx = 0
        self.timeout_count = 0
        self.invalid_start = 0
        self.test_inbuf = list()
        self.inbuf = list()
        self.time_intervals = list()
        self.DEV_streamActive.set()
        self.error_array = list()
        
        deviceData = [0 for i in range(8)]
        
        # clear tcp inbuf
        #self.conn.recv(2048) # this is not a proper flush, rx size should be set to match
        self.flush_TCP()
        
        diff = 3
        
        while self.DEV_streamActive.is_set():
            try:
                self.pre_rx += 1
                # TODO Receive and unpack sample from TCP connection
                ready = select.select([self.conn], [], [] , 0)
                if (ready[0]):
                    self.data = self.conn.recv(24+diff)
                    self.rx_count += 1     
                    if (len(self.data) == 27):
                        if (ord(self.data[0]) == 0xf and ord(self.data[1]) == 0xf and ord(self.data[2]) == 0xf):
            
                            self.test_inbuf += [self.data]
                            
                            #self.inbuf += [ord(self.data)] # #TODO this is suspect since ord should only take 1 character, and will fill quick
                            
                            # Populate fresh channel data into self.mysample
                            for j in xrange(8):
                                deviceData[j] = [self.data[diff+(j*3):diff+(j*3+3)]] 
                                val = 0
                                for s,n in list(enumerate(deviceData[j][0])):
                                    try:
                                        val ^= ord(n) << ((2-s)*8)
                                    except ValueError as e:
                                        print("value error",e)
                                    except TypeError as e:
                                        print("value error",e)
                                val = twos_comp(val)
                                self.mysample[j] = val
                            
                            self.sqwave += [self.data]
                            self.outlet.push_sample(self.mysample)
                            self.reads += 1
                            
                            #TODO count interval
                            self.count_time_interval()
                            
                        else:
                            self.invalid_start += 1
                
            except socket.timeout:
                self.timeout_count += 1
                
           
                
#==============================================================================
#             except socket.error as e:
#                 self.error_array += [e]
#==============================================================================
                
#==============================================================================
#             except:
#                 self.unknown_stream_errors += 1
#==============================================================================
                
        
    def generic_tcp_command_BYTE(self, cmd, extra = ''):
        ###############################################################################
        # Get adc status
        ###############################################################################
        if not self.IS_CONNECTED or (self.DEV_streamActive.is_set() and "ADC_start_stream" not in cmd):
            return "ILLEGAL: Must be connected and not streaming"
        try:
            self.flush_TCP()
            self.conn.send((chr(TCP_COMMAND[cmd]) + extra + chr(127)).encode('utf-8'))
            time.sleep(0.05)
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
            r_string = self.conn.recv(72)
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
        
    def initiate_TCP_stream(self):
        ###############################################################################
        # Begin TCP adc stream
        ###############################################################################

        # Start TCP rcv thread
        self.LSL_Thread = Thread(target=self.DEV_printTCPStream)
        self.LSL_Thread.start()
        self.DEV_streamActive.set()  
        # Send command to being 
        self.begin = time.time()
        return self.generic_tcp_command_OPCODE(0x03) # begins streaming TCP
        
    def initiate_TCP_stream_direct(self):
        ###############################################################################
        # Begin TCP adc stream
        ###############################################################################
        self.DEV_streamActive.set()  
        # Send command to being 
        self.begin = time.time()
        self.generic_tcp_command_OPCODE(0x03)
        self.DEV_printTCPStream()

        
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
        if not drops: avail = 0
        else: avail = ((1.0 - ((drops * 1.0) / len(self.inbuf)))*100.0)
        pckt_rate = len(self.inbuf)/(self.end-self.begin)
        return "Not Streaming", str(pckt_rate),  str(avail), str(len(self.inbuf)), str(drops)
        
    def terminate_TCP_stream(self):
        ###############################################################################
        # End UDP adc stream
        ###############################################################################
        
        #TODO NEED terminatino ACK, if NACK then resend termination command        
        
        try:
            self.generic_tcp_command_OPCODE(0xf)
            
        except: #Make specific to error: [Errno 9] Bad file descriptor
            print("Exception occured upon attempting stream termination")
            
        self.end = time.time()
        self.DEV_streamActive.clear()
        time.sleep(0.01)
        drops = self.get_drop_rate()
        if not drops: avail = 0
        else: avail = ((1.0 - ((drops * 1.0) / len(self.inbuf)))*100.0)
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
        if not self.IS_CONNECTED or self.DEV_streamActive.is_set():
            return "ILLEGAL: Must be connected and not streaming"
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
        if total_pckts == 0: return False
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
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('', self.UDP_PORT))
            s.settimeout(0.05) #TODO this blocking causes slight lag while active
            data,addr = s.recvfrom(1024)
            s.close()
            if "I_AM_ALPHA_SCAN" in data:
                return True
        except:
            pass
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
    
    def ADC_send_hex_cmd(self,cmd):
        self.generic_tcp_command_BYTE("ADC_send_hex_cmd", chr(cmd))
        
    def count_time_interval(self):
        self.time_beta = time.time()
        self.time_interval_count += 1
        try:        
            if (self.inbuf[-1] == (self.inbuf[-2] + 1)):
                self.time_intervals += [self.time_beta - self.time_alpha]
        except:
            pass
        self.time_alpha = self.time_beta
            
                
    
    
    
def unpack_data(data):
    deviceData = [list() for i in range(8)]
    for j in xrange(8):
        deviceData[j] = [data[3+(j*3):3+(j*3+3)]] 

        val = 0
        for s,n in list(enumerate(deviceData[j][0])):
            try:
                val ^= ord(n) << ((2-s)*8)
            except ValueError as e:
                print("value error",e)
            except TypeError as e:
                print("value error",e)
                
        
        val = twos_comp(val)
        print(val)
        #self.mysample[j] = val
    
    
    
    
    
    
#==============================================================================
#     
# 
# 
# =======
# # Server code for streaming tcp connection
# import socket
# import time
# from threading import Thread, Event
# from pylsl import StreamInfo, StreamOutlet
# import random
# from CommandDefinitions import *
# 
# class AlphaScanDevice:
#     
#     def __init__(self):
# 
#         ###############################################################################
#         # TCP Settings
#         ###############################################################################
#         self.TCP_IP = ''
#         self.TCP_PORT = 50007                 #CONFIGURABLE
#         self.user_input = ''
#         self.data = ''
#         
#         ###############################################################################
#         # UDP Settings
#         ###############################################################################
#         self.UDP_IP = "192.168.1.17"      #This gets over written dynamically
#         self.UDP_PORT = 2390              #CONFIGURABLE
#         
#         self.num = 10
#         self.MESSAGE = chr(self.num)
#         self.num_iter = self.num * 100
#         self.skips = 0
#         self.reads = 0
#         self.DEV_streamActive = Event()
#         self.DEV_streamActive.clear()
#         self.DEV_log = list()
#         self.inbuf = list()  
#         self.unknown_stream_errors = 0
#         self.begin = 0
#         self.end = 0
#         self.IS_CONNECTED = False
#         self.time_alpha = 0
#         self.time_beta = 0
#         self.time_intervals = list()
#         self.time_interval_count = 0
#         self.new_sample = None
#         
#         self.sqwave = list()
#         
#         
#         self.info = StreamInfo('AlphaScan', 'EEG', 8, 500, 'float32', str(time.time()))
#         self.outlet = StreamOutlet(self.info)
#         self.mysample = [random.random(), random.random(), random.random(),
#             random.random(), random.random(), random.random(),
#             random.random(), random.random()]
#             
#         self.SysParams = {'vcc':None,
#                           'free_heap':None,
#                           'mcu_chip_id':None,
#                           'sdk_ver':None,
#                           'boot_ver':None,
#                           'boot_mode':None,
#                           'cpu_freq_mhz':None,
#                           'flash_chip_id':None,
#                           'flash_chip_real_size':None,
#                           'flash_chip_size':None,
#                           'flash_chip_speed':None,
#                           'flash_chip_mode':None,
#                           'free_sketch_space':None}
#         # Debug port variables
#         self.debug_port_open = False
#         self.debug_port_no = 2391
#         #self.open_debug_port()
#         
#         self.raw_map = ""
#         self.reg_map = [[False for i in range(8)] for j in range(24)]
#         
#         
#     def open_debug_port(self):
#         try:
#             self.debug_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#             self.debug_sock.bind(('',self.debug_port_no))
#             self.debug_sock.settimeout(0)
#             self.debug_port_open = True
#             return True
#         except:
#             return False
#     
#     def close_debug_port(self):
#         try:
#             self.debug_sock.close()
#             self.debug_port_open = False
#             return True
#         except:
#             return False
#     
#     def read_debug_port(self):
#         if not self.debug_port_open: return False
#         try:
#             r = self.debug_sock.recv(1024)
#             if len(r) > 0:
#                 return r
#         except:
#             return False
#         
#     def init_TCP(self):
#         ###############################################################################
#         # Initialize TCP Port
#         ###############################################################################
#         self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
#         
#         self.s.bind((self.TCP_IP,self.TCP_PORT)) 
#         # error: [Errno 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
#         
#         self.s.settimeout(2)
#         self.s.listen(1)        
#         try:
#             self.conn,addr = self.s.accept()
#             self.conn.settimeout(.05)
#             time.sleep(0.01) # time for device to respond
#             self.UDP_IP = addr[0]
#             self.IS_CONNECTED = True
#             return True
#         except:
#             self.IS_CONNECTED = False
#             return False
#             
#     def close_TCP(self):
#         ################################################################################
#         # Close TCP connection
#         ################################################################################
#         try:
#             self.conn.close() #conn might not exist yet
#             self.s.close()
#             self.IS_CONNECTED = False
#         except:
#             pass        
#         
#     def close_UDP(self):
#         ################################################################################
#         # Close UDP connection
#         ################################################################################
#         try:
#             self.sock.close() 
#         except:
#             pass
#     
#     def DEV_printStream(self):
#         ###############################################################################
#         # UDP Stream thread target
#         ###############################################################################
# 
#         self.skips = 0
#         self.reads = 0
#         self.unknown_stream_errors = 0
#         self.time_interval_count = 0
#         self.inbuf = list()
#         self.time_intervals = list()
#         self.DEV_streamActive.set()
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.sock.bind(('',self.UDP_PORT))
#         self.sock.settimeout(0)
#         while self.DEV_streamActive.is_set():
#             try:
#                 self.data = self.sock.recv(128)
#                 self.inbuf += [ord(self.data[27:])]
#                 self.new_sample = self.parse_data_packet(self.data)
#                 self.outlet.push_sample(self.new_sample)
#                 self.sqwave += [self.new_sample]
#                 self.reads += 1
#                 
#                 #TODO count interval
#                 self.count_time_interval()
#                 
#             except socket.error as e:
#                 if e.errno == 10035:
#                     self.skips += 1
#                 elif e.errno == 9:
#                     self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#                     self.sock.bind(('',self.UDP_PORT))
#                     self.sock.settimeout(0)
#             except:
#                 self.unknown_stream_errors += 1
#     
#     def twos_comp(self, val, bits=24):
#         """compute the 2's compliment of int value val"""
#         if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
#             val = val - (1 << bits)        # compute negative value
#         return val
#         
#     def parse_data_packet(self, data):
#         chanData = data[3:27]
#           
#         deviceData = list()
#         for j in xrange(8):
#             deviceData += [chanData[j*3:j*3+3]]
#             val = 0
#             for s,n in list(enumerate(reversed(deviceData[j]))):
#                 val ^= ord(n) << (s*8)
#             deviceData[j] = float(self.twos_comp(val))
#         return deviceData
#     
#     
#         
#     def generic_tcp_command_BYTE(self, cmd, extra = ''):
#         ###############################################################################
#         # Get adc status
#         ###############################################################################
#         if not self.IS_CONNECTED or (self.DEV_streamActive.is_set() and "ADC_start_stream" not in cmd):
#             return "ILLEGAL: Must be connected and not streaming"
#         try:
#             self.flush_TCP()
#             self.conn.send((chr(TCP_COMMAND[cmd]) + extra + chr(127)).encode('utf-8'))
#             time.sleep(0.05)
#             r_string = self.conn.recv(64)
#         except:
#             r_string = 'no_response'
#         return r_string
#         
#     def generic_tcp_command_OPCODE(self, opcode, extra = ''):
#         ###############################################################################
#         # Get adc status
#         ###############################################################################
# 
#         self.flush_TCP()
#         self.conn.send((chr(opcode) + extra + chr(127)).encode('utf-8'))
#         time.sleep(0.05)
#         try:
#             r_string = self.conn.recv(64)
#         except:
#             r_string = 'no_response'
#         return r_string
#         
#     def generic_tcp_command_STRING(self, txt):
#         ###############################################################################
#         # Get adc status
#         ###############################################################################
# 
#         self.flush_TCP()
#         self.conn.send((txt + chr(127)).encode('utf-8'))
#         time.sleep(0.05)
#         try:
#             r_string = self.conn.recv(64)
#         except:
#             r_string = 'no_response'
#         return r_string
#         
#     def read_tcp(self, num_bytes=64):
#         try:
#             r_string = self.conn.recv(num_bytes)
#         except:
#             r_string = 'no_response'
#         return r_string
#     
#     def pull_adc_registers(self): 
#         ###############################################################################
#         # Get all registers and return as list of lists
#         ###############################################################################
#         # send generic command to retrieve adc registers
#         self.generic_tcp_command_BYTE("ADC_get_register")
#         # wait for response, loop a few times to account for possible delay then timeout
#         for i in range(4):
#             time.sleep(0.05)
#             r = self.read_tcp(num_bytes=2048) # ensure this is enough to get whole map
#             print(r)
#             if (len(r) > 24) and ("bbb" in r) and ("eee" in r):
# 
#                 self.raw_map = r[r.find("bbb")+len("bbb"):r.find("eee")]
#                 assert(len(self.raw_map) == 24)               
#                 for i in range(len(self.raw_map)):
#                     for j in range(8):
#                         if (ord(self.raw_map[i]) & (0x1 << j) ):
#                             self.reg_map[i][j] = True
#                         else:
#                             self.reg_map[i][j] = False
#                 
#                 return self.reg_map              
#                 
#                 # return map
#             else:
#                 continue
#         
#         return False # Create better error message here, or use proper exception handling...
#         
#     def push_adc_registers(self, RegMap):
#         #TODO push real register map to device
#         
#         #Build byte characters from reg map
#         byte_list = [0 for i in range(24)]
#         for i in range(24):
#             for j in range(8):
#                 if RegMap[i][j]:
#                     byte_list[i] |= (0x1 << j)
#         
#         self.chr_map = ','.join([str(n) for n in byte_list])
#         
#         r = self.generic_tcp_command_BYTE('ADC_set_register','bbb'+self.chr_map+'eee')
#         #r = self.generic_tcp_command_BYTE('ADC_set_register', 'bbbhi_there my name is stream shady and i like to cream ladies eee')
#         
#         return r
#         
#             
# 
#     def initiate_UDP_stream(self):
#         ###############################################################################
#         # Begin UDP adc stream
#         ###############################################################################
# 
#         # Start UDP rcv threyad
#         self.LSL_Thread = Thread(target=self.DEV_printStream)
#         self.LSL_Thread.start()
#         self.DEV_streamActive.set()  
#         # Send command to being 
#         self.begin = time.time()
#         return self.generic_tcp_command_BYTE("ADC_start_stream")
#         
#     def terminate_UDP_stream(self):
#         ###############################################################################
#         # End UDP adc stream
#         ###############################################################################
#         
#         #TODO NEED terminatino ACK, if NACK then resend termination command        
#         
#         try:
#             self.sock.sendto(('ttt'.encode('utf-8')), (self.UDP_IP, self.UDP_PORT))
#             
#         except: #Make specific to error: [Errno 9] Bad file descriptor
#             self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#             #self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192)
#             self.sock.bind(('',self.UDP_PORT))
#             self.sock.settimeout(0)
#             self.sock.sendto(('ttt'.encode('utf-8')), (self.UDP_IP, self.UDP_PORT))
#         self.end = time.time()
#         self.DEV_streamActive.clear()
#         time.sleep(0.01)
#         self.sock.close()
#         drops = self.get_drop_rate()
#         if not drops: avail = 0
#         else: avail = ((1.0 - ((drops * 1.0) / len(self.inbuf)))*100.0)
#         pckt_rate = len(self.inbuf)/(self.end-self.begin)
#         return "Not Streaming", str(pckt_rate),  str(avail), str(len(self.inbuf)), str(drops)
#     
#     
#     def flush_TCP(self):
#         ###############################################################################
#         # Clear TCP input buffer
#         ###############################################################################
#         try:
#             self.conn.recv(self.conn.getsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF))
#         except:
#             pass
#     
#     def flush_UDP(self):
#         ###############################################################################
#         # Clear udp input buffer
#         ###############################################################################
#         try:
#             self.sock.recv(65535)
#         except:
#             pass
#     
#     def update_adc_registers(self,reg_to_update):
#         #send adc registers to update over tcp
#         self.flush_TCP()
#         self.conn.send('u'+''.join([str(t) for t in reg_to_update])+chr(127).encode('utf-8'))
#         time.sleep(0.01) # Time for device to respond
#         return
# 
#     def update_command_map(self):
#         # create csv string from command map dict
#         if not self.IS_CONNECTED or self.DEV_streamActive.is_set():
#             return "ILLEGAL: Must be connected and not streaming"
#         self.flush_TCP()
#         self.conn.send((chr(TCP_COMMAND["GEN_update_cmd_map"]) + "_begin_cmd_map_" + str(TCP_COMMAND) + ',  '+chr(127)).encode('utf-8')) #NOTE: comma is necessary
#         time.sleep(0.01)
#         try:
#             r_string = self.conn.recv(64)
#         except:
#             r_string = 'no_response'
#         return r_string
#         
#     def get_drop_rate(self):
#         i = 0
#         drops = 0
#         total_pckts = len(self.inbuf)
#         if total_pckts == 0: return False
#         for n in self.inbuf:
#             if i != n:
#                 drops += 1
#                 i = n
#             if i == 255: #wrap around
#                 i = 0
#             else:
#                 i += 1
#         # return success rate
#         return drops
#     
#     def broadcast_disco_beacon(self):
#         # send broadcast beacon for device to discover this host
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#         s.sendto('alpha_scan_beacon_xbx_'+str(self.TCP_PORT)+'_xex',('192.168.1.255',self.UDP_PORT)) #TODO this subnet might not work on all LAN's (see firmware method)
#         # send desired TCP port in this beacon 
#         s.close();
#         
#     def listen_for_device_beacon(self):   
#         try:
#             s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#             s.bind(('', self.UDP_PORT))
#             s.settimeout(0.05) #TODO this blocking causes slight lag while active
#             data,addr = s.recvfrom(1024)
#             s.close()
#             if "I_AM_ALPHA_SCAN" in data:
#                 return True
#         except:
#             pass
#         return False
#         
#     def connect_to_device(self):
#         self.broadcast_disco_beacon()
#         return self.init_TCP()
#         
#     def set_udp_delay(self, delay):
#         extra = "_b_"+str(delay)+"_e_"
#         return self.generic_tcp_command_BYTE("ADC_set_udp_delay", extra)
#     
#     def parse_sys_commands(self):
#         #read tcp buff
#         buf = self.read_tcp(1024)
#         #check for complete system params respons
#         if ('begin_sys_commands' not in buf) or ('end_sys_commands' not in buf):
#             return False
#         #else begin parsing
#         buf_arr = buf.split(",")
#         for e in buf_arr:
#             for k in self.SysParams.keys():
#                 if k in e:
#                     self.SysParams[k] = e[e.find(":")+1:]
#                     break
#         return True
#     
#     def ADC_send_hex_cmd(self,cmd):
#         self.generic_tcp_command_BYTE("ADC_send_hex_cmd", chr(cmd))
#         
#     def count_time_interval(self):
#         self.time_beta = time.time()
#         self.time_interval_count += 1
#         try:        
#             if (self.inbuf[-1] == (self.inbuf[-2] + 1)):
#                 self.time_intervals += [self.time_beta - self.time_alpha]
#         except:
#             pass
#         self.time_alpha = self.time_beta
#             
#                 

#     
#==============================================================================
