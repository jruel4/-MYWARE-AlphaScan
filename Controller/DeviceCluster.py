from AlphaScanController import AlphaScanDevice

class DeviceCluster:
    """
    The DeviceCluster class serves to coordinate the control of multiple 
    AlphaScan Devices. The GUI should never directly call AlphaScanDevice
    methods, it should go through the Device cluster instead.
    """
    
    def __init__(self, num_devices = 1):
        self.dev = [AlphaScanDevice() for i in range(num_devices)]
    
    def open_debug_port(self):
        pass
    
    def close_debug_port(self):
        pass
    
    def read_debug_port(self):
        pass
        
    def init_TCP(self):
        pass
            
    def close_TCP(self):
        pass
        
    def close_UDP(self):
        pass
                
    def generic_tcp_command_BYTE(self, cmd, extra = ''):
        pass
        
    def generic_tcp_command_OPCODE(self, opcode, extra = ''):
        pass
    
    def generic_tcp_command_STRING(self, txt):
        pass
        
    def read_tcp(self, num_bytes=64):
        pass	

    def pull_adc_registers(self): 
        pass
 
    def push_adc_registers(self, RegMap):
        pass	
	
    def sync_adc_registers(self):
        pass

    def initiate_UDP_stream(self):
        pass
        
    def initiate_TCP_stream(self):
        pass
        
    def initiate_TCP_streamX(self):
        pass
        
    def initiate_TCP_stream_direct(self):
        pass
        
    def terminate_UDP_stream(self):
        pass
        
    def terminate_TCP_stream(self):
        pass
    
    def flush_TCP(self):
        pass
    
    def flush_UDP(self):
        pass
    
    def update_adc_registers(self,reg_to_update):
        pass

    def update_command_map(self):
        pass
        
    def get_drop_rate(self):
        pass
    
    def broadcast_disco_beacon(self):
        pass
        
    def listen_for_device_beacon(self):   
        pass
        
    def connect_to_device(self):
        pass
        
    def set_udp_delay(self, delay):
        pass
    
    def parse_sys_commands(self):
        pass
    
    def ADC_send_hex_cmd(self,cmd):
        pass
        
    def count_time_interval(self):
        pass
            
    def close_udp_solo(self):
        pass
    
            
            
          
          
          
          
          