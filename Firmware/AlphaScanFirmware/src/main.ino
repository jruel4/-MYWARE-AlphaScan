////////////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////////////
#include <ESP8266WiFi.h>
#include <SPI.h>
#include <Wire.h>
#include <WiFiUDP.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include "FS.h"
#include <map>

////////////////////////////////////////////////////////////////////////////////
// Global variables
////////////////////////////////////////////////////////////////////////////////
char ssid[20];                          //
char password[50];                      //
IPAddress host_ip;                      //

String ssid_str;                        //
String password_str;                    //
String host_ip_str;                     //

bool ssid_set     = false;              //
bool password_set = false;              //
bool host_ip_set  = true;               //
bool network_set  = false;              //

int TCP_port;                           //
int UDP_port = 2390;                    //

int UDP_Stream_Delay = 1500;            //
byte packetBuffer[64];                  //
WiFiClient client;                      //
WiFiUDP Udp;                            //
String rx_buf_string;                   //
char rx_buf[1024];                      //
char localIpString[24];                 //
bool open_a = true;                     //
File f;                                 //

const char network_parameters_path[] = "/neti_params.txt"; //
const char command_map_path[]        = "/command_map.txt"; //
String firmware_version              = "0.0.3";            //

enum T_SYSTEM_STATE {
  AP_MODE,
  RUN_MODE
} SYSTEM_STATE;

std::map<uint8_t, String> COMMAND_MAP_2_str;
std::map<String, uint8_t> COMMAND_MAP_2_int;


////////////////////////////////////////////////////////////////////////////////
// ADS1299 SPI OPCODES
////////////////////////////////////////////////////////////////////////////////
const uint8_t ADS_WAKEUP  = (0x02); //wakeup
const uint8_t ADS_STANDBY = (0x04); //standby
const uint8_t ADS_RESET   = (0x06); //reset
const uint8_t ADS_START   = (0x08); //start
const uint8_t ADS_STOP    = (0x0A); //stop
const uint8_t ADS_RDATAC  = (0x10); //read data continuous
const uint8_t ADS_SDATAC  = (0x11); //stop read data continuous
const uint8_t ADS_RDATA   = (0x12); //read data by command
const uint8_t ADS_RREG_1  = (0x20); //read reg start at register 0
const uint8_t ADS_RREG_2  = (0x17); //read all 24 register(s)
const uint8_t ADS_WREG_1  = (0x40); //write registers starting at 0
const uint8_t ADS_WREG_2  = (0x00); //write one register

uint8_t AdsMap[24]        = {0};    //map of ADS registers
int DRDY_PIN = 1;//IO1

////////////////////////////////////////////////////////////////////////////////
// BQ25120 Constants
////////////////////////////////////////////////////////////////////////////////
const uint8_t BQ_7_ADDR = 0x6A; // 7 bit I2C address
const uint8_t BQ_8_ADDR = 0xD4; // 8 bit I2C address

uint8_t BQ_Reg_Map[12];
uint8_t BQ_Set_Reg[12];

////////////////////////////////////////////////////////////////////////////////
// Function prototype declarations
////////////////////////////////////////////////////////////////////////////////
void WiFi_EstTcpHostConn();
void ADC_StartDataStream();
void ADC_GetRegisterContents();
void WiFi_ProcessTcpClientRequest();
void AP_SupportRoutine();
void FS_ReadFsNetParams();
void AP_ReadNetParams();
void WiFi_ConnectToWan();
void OTA_Handle();
void OTA_Setup();
void GEN_Setup();
void FS_LoadCommandMap();
void GEN_LoadDefaultCommandMap();
void GEN_CopyCommandMapToStr();
bool GEN_ParseCommandMap();
void FS_SaveCommandMap();
void WiFi_ListenUdpBeacon();
void ADC_SetUdpDelay();
void FS_Format();
void FS_SendCommandMap();
void FS_GetFsInfo();
void FS_SendNetParams();
void ADC_SetupSPI();
void ADC_CloseSPI();
void ADC_ReadRegisters();
void BQ_Setup();
void BQ_handleFaultISR();
void BQ_readRegister(uint8_t reg_addr, int num_reg, uint8_t* BQ_Reg_Map);
void BQ_writeRegister(uint8_t reg_addr, int num_reg, uint8_t* BQ_Set_Reg);
String GEN_ExtractNetParams(String,String);

////////////////////////////////////////////////////////////////////////////////
// Function definitions
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// Primary Subroutines
////////////////////////////////////////////////////////////////////////////////
void setup() {

  GEN_Setup();
  FS_LoadCommandMap();
  FS_ReadFsNetParams();
  AP_ReadNetParams();
  WiFi_ConnectToWan();
  WiFi_ListenUdpBeacon();
}

void loop() {

  switch (SYSTEM_STATE) {
    case AP_MODE:
    {
      AP_ReadNetParams();
      WiFi_ConnectToWan();
      break;
    }
    case RUN_MODE:
    {
      WiFi_EstTcpHostConn();
      WiFi_ProcessTcpClientRequest();
      break;
    }
    default:
    {
      Serial.println("Invalid SYSTEM_STATE");
      break;
    }
  }

}

////////////////////////////////////////////////////////////////////////////////
// Secondary Subroutines
////////////////////////////////////////////////////////////////////////////////
void GEN_Setup() {

  Serial.begin(74880);
  Serial.println("");
  Serial.println("Firmware version: "+firmware_version);


}

bool GEN_ParseCommandMap() {

  // loop over string contents until key,value pairs are exhausted
  //Serial.print("low level buf: ");int i; for (i=0; i<1024; i++) {Serial.print(rx_buf[i]);}
  Serial.print("Rx Map: "); Serial.println(rx_buf_string);

  std::map<uint8_t, String> new_map;
  int begin = 1;
  int end = 0;
  String cmd_pair;

  // debuf values
  String key;
  int value;

  while (end > -1) {

    Serial.println("Processing k,v pair...");

    end = rx_buf_string.indexOf(',',begin+1); // not sure if search include begin index

    Serial.print("found end:   "); Serial.println(end);
    Serial.print("found begin: "); Serial.println(begin);

    if (end > -1) {
      cmd_pair = rx_buf_string.substring(begin, end);
      Serial.print("cmd_pair: "); Serial.println(cmd_pair);
      // search for single quotes to extract key
      key = cmd_pair.substring(cmd_pair.indexOf("'")+1, cmd_pair.lastIndexOf("'")); // NOTE: might need to escape backslash
      Serial.print("key: ");Serial.println(key);
      // search for colon to find value
      value = (cmd_pair.substring(cmd_pair.indexOf(":")+2, end - 1)).toInt();
      Serial.print("value: "); Serial.println(value);

      // TODO check for general validity of k,v pair, if invalid then continue
      // if (key == 0) continue;

      // Add new k,v pair to new_map
      new_map[value] = key;

      // update begin index
      begin = end;
    }
  }

  if (new_map.size() < 5) {
    Serial.println("map validation failed");
    return false;
  }

  // set COMMAND_MAP_2_str to new_map
  COMMAND_MAP_2_str = new_map;

  // copy command map inverse
  GEN_CopyCommandMapToStr();

  Serial.println("Finished parsing new map.");
  return true;
}

void GEN_LoadDefaultCommandMap() {

  Serial.println("loading default command map");
  COMMAND_MAP_2_str[1] = "GEN_get_status";
  COMMAND_MAP_2_str[2] = "GEN_start_ota";
  COMMAND_MAP_2_str[3] = "GEN_start_ap";
  COMMAND_MAP_2_str[4] = "ADC_start_stream";
  COMMAND_MAP_2_str[5] = "ADC_stop_stream";
  COMMAND_MAP_2_str[6] = "ADC_get_register";
  COMMAND_MAP_2_str[7] = "ADC_update_register";
  COMMAND_MAP_2_str[8] = "ACC_get_status";
  COMMAND_MAP_2_str[9] = "PWR_get_status";
  COMMAND_MAP_2_str[10] = "FS_Format_fs";

  GEN_CopyCommandMapToStr();
}

void GEN_CopyCommandMapToStr() {
  // takes <uint8_t,String> and flip copies to <String, uint8_t>
  typedef std::map<uint8_t, String>::iterator it_type;
  for (it_type iterator = COMMAND_MAP_2_str.begin(); iterator != COMMAND_MAP_2_str.end(); iterator++) {
    COMMAND_MAP_2_int[iterator->second] = iterator->first;
  }
}

String GEN_ExtractNetParams(String Request, String delimeter) {
  // Standard request syntax is "delimeter_value_enddelimeter"
  // This method extracts "value"
  return Request.substring( (Request.indexOf(delimeter) + delimeter.length() + 1), Request.indexOf("end"+delimeter) - 1);
}

////////////////////////////////////////////////////////////////////////////////
// WiFi
////////////////////////////////////////////////////////////////////////////////
void WiFi_ConnectToWan() {

  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempts++;

    if (attempts > 30) { // may want to tune this number up for poor connections
      Serial.println("WiFi parameters appear to be invalid, switching to AP Mode...");
      SYSTEM_STATE = AP_MODE;
      return;
    }
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  IPAddress myIP = WiFi.localIP();
  sprintf(localIpString, "%d.%d.%d.%d", myIP[0], myIP[1], myIP[2], myIP[3]);
  Serial.println(localIpString);

  Udp.begin(UDP_port);

  SYSTEM_STATE = RUN_MODE;
}

void WiFi_ProcessTcpClientRequest() {
  int i;
  // Check for command from host
  int avail = client.available();

  if (avail) {
    for (i=0; i < avail; i++) {
        rx_buf[i] = client.read();
    }
    rx_buf[avail] = '\0';
  }
  else {
    return;
  }

  rx_buf_string = String("");
  for (i=0; i<avail; i++) {
    rx_buf_string += rx_buf[i];
  }

  // Extract command byte
  uint8_t cmd = (uint8_t) rx_buf[0];
  Serial.print("Executing command: "); Serial.println(COMMAND_MAP_2_str[cmd]);

  ////////////////////////////////////////////////////////////////////////////
  if (cmd ==  0x00) // Update command map -- this is always command 0x00
  {

    Serial.println("updating command map...");
    client.print("updating map command");
    delay(10);
    if (GEN_ParseCommandMap()) {
      FS_SaveCommandMap();
    }
    else {
      Serial.println("map map parse failed");
    }
  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd ==  0x01) //OTA update
  {
    client.print("Entering OTA Mode"); // NOTE might need more wait that this... since we then shutfown current WiFi setup
    delay(10);
    OTA_Handle();

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd == 0x02) // Alive query
  {
    client.print("_ALIVE_ACK_");
  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd ==  COMMAND_MAP_2_int["ADC_start_stream"]) //start streaming adc data
  {
    client.print("Initializing ADC stream");
    delay(1);
    ADC_StartDataStream();

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd ==  COMMAND_MAP_2_int["ADC_get_register"]) // get ADS1299 registers
  {
    ADC_GetRegisterContents();

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd ==  COMMAND_MAP_2_int["ADC_stop_stream"]) //stop streaming adc data
  {
    // this command does nothing in this context

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd ==  COMMAND_MAP_2_int["ACC_get_status"]) //read accelerometer data
  {
    client.print("Here is your accelerometer data");

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd ==  COMMAND_MAP_2_int["PWR_get_status"]) //read pwr data
  {
    client.print("Here is your power data");

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd ==  COMMAND_MAP_2_int["GEN_get_status"]) //information request
  {
    client.print("Dear host, here is your information");

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd ==  COMMAND_MAP_2_int["ADC_update_register"]) //update register contents
  {
    Serial.println("Received request to update ADC registers");

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd ==  COMMAND_MAP_2_int["GEN_start_ap"]) //AP mode
  {
    client.stop();
    delay(1);
    Serial.println("Forcing AP Mode");
    SYSTEM_STATE = AP_MODE;
    network_set = host_ip_set = ssid_set = password_set = false;

  }

  ////////////////////////////////////////////////////////////////////////////
  else if(cmd == COMMAND_MAP_2_int["GEN_get_dev_ip"])
  {
    // send currently allocated device IP
    Serial.print("sending back local ip: "); Serial.println(localIpString);
    client.print(localIpString);

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd == COMMAND_MAP_2_int["GEN_listen_beacon"])
  {
    WiFi_ListenUdpBeacon();
  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd == COMMAND_MAP_2_int["ADC_set_udp_delay"])
  {
    Serial.println("setting udp stream delay");
    ADC_SetUdpDelay();
  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd == COMMAND_MAP_2_int["FS_format_fs"])
  {
    FS_Format();
  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd == COMMAND_MAP_2_int["FS_get_net_params"])
  {
    FS_SendNetParams();
  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd == COMMAND_MAP_2_int["FS_get_fs_info"])
  {
    FS_GetFsInfo();
  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd == COMMAND_MAP_2_int["FS_get_command_map"])
  {
    FS_SendCommandMap();
  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd == COMMAND_MAP_2_int["GEN_get_sys_params"])
  {
    client.print("Retrieving parameters, please wait about 10 seconds...");
    Serial.println("retrieving system parameters");

    //retrieve system parameters
    client.print("begin_sys_commands");
    client.print(",vcc:");
    client.print(ESP.getVcc());

    client.print(",free_heap:");
    client.print(ESP.getFreeHeap());

    client.print(",mcu_chip_id:");
    client.print(ESP.getChipId());

    client.print(",sdk_ver:");
    client.print(ESP.getSdkVersion()); //NOTE this string length should be enough...

    client.print(",boot_ver:");
    client.print(ESP.getBootVersion());

    client.print(",boot_mode:");
    client.print(ESP.getBootMode());

    client.print(",cpu_freq_mhz:");
    client.print(ESP.getCpuFreqMHz());

    client.print(",flash_chip_id:");
    client.print(ESP.getFlashChipId());

    //gets the actual chip size based on the flash id
    client.print(",flash_chip_real_size:");
    client.print(ESP.getFlashChipRealSize());

    //gets the size of the flash as set by the compiler
    client.print(",flash_chip_size:");
    client.print(ESP.getFlashChipSize());

    client.print(",flash_chip_speed:");
    client.print(ESP.getFlashChipSpeed());

    client.print(",flash_chip_mode:");
    client.print(ESP.getFlashChipMode());

    client.print(",end_sys_commands");
    Serial.println("finished sending systems params to host.");

  }

  ////////////////////////////////////////////////////////////////////////////
  else if (cmd == COMMAND_MAP_2_int["GEN_reset_device"])
  {
    Serial.println("Resetting Device");
    client.print("Resetting Device");
    ESP.reset(); // difference between reset and restart?
  }

  ////////////////////////////////////////////////////////////////////////////
  else
  {
    Serial.print("Unknown Command");
  }

}

void WiFi_ListenUdpBeacon() {

  volatile uint64_t cnt = 0;
  int noBytes = 0;
  char inbuf[50];
  IPAddress broadcastIp = ~WiFi.subnetMask() | WiFi.gatewayIP();
  Serial.print("broadcast IP: ");Serial.println(broadcastIp);
  Serial.println("Listening for broadcast beacon.");

  while(1)
  {
    cnt++;
    noBytes = Udp.parsePacket();

    if ( noBytes ) {
      Udp.read(inbuf,noBytes);
      Serial.print("RX: ");
      Serial.println(inbuf);
      Serial.println("... finished.");
      String valCheck = String(inbuf);
      // check if this is host beacon
      if (valCheck.indexOf("alpha_scan_beacon") > -1) {
        Serial.println("found alpha scan host");

        host_ip = Udp.remoteIP();
        UDP_port = Udp.localPort(); // host will listen on same port that it sent to

        Serial.println(host_ip);
        Serial.println(UDP_port);

        // extract tcp port to connect to from beacon message
        TCP_port = (valCheck.substring(valCheck.indexOf("xbx_")+4, valCheck.indexOf("_xex"))).toInt();
        Serial.print("tcp_port: "); Serial.println(TCP_port);

      }
      break;
    }

    else if ( (cnt % 10000) == 0 ) { // TODO don't flood network indefinitely...
      // Broadcast alive beacon so that control app knows to auto connect
      Udp.beginPacket(broadcastIp, 2390);
      Udp.write("_I_AM_ALPHA_SCAN_");
      Udp.endPacket();
      delay(1);
      if ( (cnt % 100000 ) == 0 ) {
        Serial.print(".");
      }
    }
  }
}

void WiFi_EstTcpHostConn() {

  if (!client.status()) {

    Serial.print("host_ip: ");Serial.println(host_ip);
    Serial.print("port: ");Serial.println(TCP_port);
    Serial.println("Attempting to connect to host.");

    // Connet to host
    while (!client.connect(host_ip,TCP_port)); // Note: this call block indefinitely - so incorrect host_ip here is fatal
    {
      Serial.println("Still attempting to connect...");
      Serial.println("wait 1 sec...");
      delay(1000);

    }
    client.print("Connected");
    Serial.println("Connected to host");
  }
}

////////////////////////////////////////////////////////////////////////////////
// SPIFFS
////////////////////////////////////////////////////////////////////////////////
void FS_ReadFsNetParams() {
  /////////////////////////////////////////////////////////////////////////////////////////////////////
  // Check SPIFFS for network parameters
  /////////////////////////////////////////////////////////////////////////////////////////////////////

  // Check to see if net_params file exists
  Serial.print("checking if exists: ");Serial.println(network_parameters_path);
  if(SPIFFS.exists(network_parameters_path)) {
    Serial.println("network_parameters_path exists");
    open_a = true;
  }
  else {
    Serial.println("network_parameters_path does not exist");
    open_a = false;
  }

  // If network_parameters_path exists, try to open file
  if (open_a) {
    f = SPIFFS.open(network_parameters_path,"r");

    // Check if file open succeeded
    if (!f) {
      Serial.println("file open failed");
      SYSTEM_STATE = AP_MODE;
      return;
    }
    else {
      Serial.println("file open SUCCESS");
    }

    // Read parameters from file
    f.seek(0,SeekSet);
    // Read SSID
    if(f.available()) {
      //Lets read line by line from the file
      ssid_str = f.readStringUntil('\n');
      ssid_str = GEN_ExtractNetParams(ssid_str,"ssid");
      strcpy(ssid,&(ssid_str[0]));
      ssid_set = true;

      Serial.print("RS_SSID: ");Serial.println(ssid);
    }

    // Read password
    if(f.available()) {
      //Lets read line by line from the file
      password_str = f.readStringUntil('\n');
      password_str = GEN_ExtractNetParams(password_str,"pass");
      strcpy(password,&(password_str[0]));
      password_set = true;

      Serial.print("RS_PASS: ");Serial.println(password);
    }

    // Read host_ip
    if(f.available()) { // NOTE: modift host ip parsing for for IPAddress type
      //Lets read line by line from the file
      host_ip_str = f.readStringUntil('\n');
      host_ip_str = GEN_ExtractNetParams(host_ip_str,"host_ip");
      //strcpy(host_ip,&(host_ip_str[0]));
      host_ip_set = true;

      Serial.print("RS_host_ip: ");Serial.println(host_ip);
    }

    f.close();

    if (ssid_set && host_ip_set && password_set)
    network_set = true;

  }
  // else procees to SoftAP Mode
  else {
    network_set = false;
  }
}

void FS_LoadCommandMap() {

  // Initiate SPIFFS
  Serial.println("inititating file SPIFFS class");
  if(SPIFFS.begin())Serial.println("Spiffs mount success");else {Serial.println("Spiffs mount FAIL");return;}

  // check if cmd file exists
  if (SPIFFS.exists(command_map_path)) {

    Serial.println("command map path exists");
  }
  else {

    // if cmd file does not exist, load default map
    Serial.println("command map path does not exist, loading default map...");
    GEN_LoadDefaultCommandMap();
    return;
  }

  // open SPIFFS file
  f = SPIFFS.open(command_map_path, "r");
  if (!f) {
    Serial.println("command file open failed");
    // load default instead
    GEN_LoadDefaultCommandMap();
    return;
  }
  else {
    Serial.println("command file open SUCCESS");
  }

  // Read parameters from file
  f.seek(0,SeekSet);

  if(f.available()) {

    //Lets read line by line from the file
    rx_buf_string = f.readStringUntil('\n');

    if (!GEN_ParseCommandMap()) {
      GEN_LoadDefaultCommandMap();
    }

  }
  else {
    Serial.println("failed to read command map string");
  }
}

void FS_Format() {
  Serial.println("beginning format");
  client.print("formatting SPIFFS");
   if (SPIFFS.format()) {
     Serial.println("format successful");
     client.print("format successful");
   }
   else {
     Serial.println("format failure");
     client.print("format failure");
   }
}

void FS_SendNetParams() {
  FS_ReadFsNetParams();
  client.print("ssid:" + ssid_str + "," + "password: " + password_str);
  Serial.println("finished getting net params");
  // NOTE may need a control method with longer block time to return this data
}

void FS_SaveCommandMap() {

  // open file
  f = SPIFFS.open(command_map_path,"w");
  if (!f) {
    Serial.println("file open failed");
    return;
  }
  else {
    Serial.println("file open SUCCESS");
  }

  // write lines
  f.seek(0,SeekSet);
  f.println(rx_buf_string);
  f.close();
  Serial.println("command map saved");
}

void FS_SendCommandMap() {
  FS_LoadCommandMap();
  client.print(rx_buf_string);
  Serial.println("finished getting command map");
}

void FS_GetFsInfo() {
  FSInfo fs_info;
  SPIFFS.info(fs_info);
  char info_str[100];
  sprintf(info_str, "totalBytes: %d, usedByted: %d, blockSize: %d, pageSize: %d, \
                     maxOpenFiles: %d, maxPathLen: %d",
                     fs_info.totalBytes, fs_info.usedBytes, fs_info.blockSize,
                     fs_info.pageSize, fs_info.maxOpenFiles, fs_info.maxPathLength);
  Serial.println(info_str);
  client.print(info_str);
}

////////////////////////////////////////////////////////////////////////////////
// Software Access Point (SoftAP)
////////////////////////////////////////////////////////////////////////////////
void AP_ReadNetParams() {

  // acquire SSID and password via SoftAP
  Serial.println("acquire SSID and other network params now...");
  while(!network_set) {

    AP_SupportRoutine();

    if (network_set) {
      // Write network params to SPIFFS

      // open file
      f = SPIFFS.open(network_parameters_path,"w");
      if (!f) {
        Serial.println("file open failed");
        return;
      }
      else {
        Serial.println("file open SUCCESS");
      }

      // write lines
      f.seek(0,SeekSet);
      f.println("ssid_" + ssid_str + "_endssid");
      f.println("pass_" + password_str + "_endpass");
      f.println("host_ip_" + host_ip_str + "_endhost_ip");
      f.close();
    }
  }

  Serial.println("Network parameters acquired, now attempting to join LAN with: ");
  Serial.println("ssid: " + ssid_str + ", pass: " + password_str );

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(1000);
}

void AP_SupportRoutine() {

  // Define local AP variables
  const char AP_NAME_STR[] = "AlphaScanAP";
  const char WiFiAPPSK[] = "martianwearables";
  String custom_response;
  long int c = 0;
  int i;
  WiFiServer server(80);

  // Setup software access point (SoftAP)
  WiFi.mode(WIFI_AP); // MAIN CALL TO SET WiFi MODE
  WiFi.softAP(AP_NAME_STR, WiFiAPPSK); // THIS IS THE MAIN CALL TO SETUP AP
  server.begin();

  // Loop and listen for client data
  // Check if a client has connected

  client = server.available();
  while (!client) {
    client = server.available();
    if(c++ % 1000000 == 0)Serial.print(".");if(c % 10000000 ==0)Serial.println("");
  }

  if (ssid_set && host_ip_set && password_set) {
    network_set = true;
    Serial.println("Network is set");
    delay(1);
    client.print("HTTP/1.1 200 OK\rfuck off");
    delay(1);
    client.stop();
    delay(1);
    return;
  }

  // Read the first line of the request
  String req = client.readStringUntil('\r'); //NOTE \r is not included in query text yet this terminates anyways...
  Serial.print("Request received: ");Serial.print(req);Serial.println("");
  client.flush();

  // Parse request

  // Alive request
  if (req.indexOf("alive") >= 0) {
    custom_response = "___IAMALPHASCAN___";
  }

  // Rx SSID
  else if (req.indexOf("ssid") >= 0) {
    // collect SSID into local variables
    ssid_str = GEN_ExtractNetParams(req,"ssid");
    strcpy(ssid,&(ssid_str[0]));
    custom_response = "SSID";
    ssid_set = true;

    Serial.print("received ssid: ");Serial.println(ssid);
  }

  // Rx passkey
  else if (req.indexOf("pass") >= 0) {
    password_str = GEN_ExtractNetParams(req,"pass");
    strcpy(password,&(password_str[0]));
    custom_response = "passkey";
    password_set = true;

    Serial.print("received pass: ");Serial.println(password);
  }

  // Rx passkey
  else if (req.indexOf("host_ip") >= 0) {
    host_ip_str = GEN_ExtractNetParams(req,"host_ip");
    //strcpy(host_ip,&(host_ip_str[0])); //NOTE use cpy method compatible with IPAddress
    custom_response = "host_ip";
    host_ip_set = true;

    Serial.print("received host_ip: ");Serial.println(host_ip);
  }

  // Echo network params
  else if (req.indexOf("echo_params") >= 0) {
    custom_response = "ssid: " + ssid_str + ", pass: " + password_str;
  }

  else {
    custom_response = "unknown_request";
  }


  // Send the response to the client
  String s = "HTTP/1.1 200 OK\r";
  s += "Content-Type: text/html\r\r";
  s += "<!DOCTYPE HTML>\r<html>\r";
  s += custom_response;
  s += "</html>\n";
  client.print(s);
  delay(1);
  Serial.println("Client disonnected");

}

////////////////////////////////////////////////////////////////////////////////
// Over The Air (OTA) Firmware Update Support
////////////////////////////////////////////////////////////////////////////////
void OTA_Setup() {
  ArduinoOTA.onStart([]() {
    Serial.println("Start");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("End");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\n", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });
  ArduinoOTA.begin();
}

void OTA_Handle() {
  // handle ota
  Serial.println("handing OTA - must either update or reset device");
  // shutdown previous tcp connections
  client.stop();
  delay(100);
  //
  OTA_Setup();
  while(1) {
    ArduinoOTA.handle();
    delay(1);
  }
}

////////////////////////////////////////////////////////////////////////////////
// Analog-to-Digial Converter (ADC)
////////////////////////////////////////////////////////////////////////////////
void ADC_SetupDefaultConfig() {}

void ADC_StartDataStream() {

  Serial.println("Initiating stream");
  int i;
  int noBytes = 0;
  uint32_t c  = 0;

  //////////////////////////////////////////
  // Setup SPI
  //////////////////////////////////////////
  uint8_t sample_buffer[26];
  ADC_SetupSPI();
  // Start read data continuous
  SPI.transfer(ADS_RDATAC);
  // Send start opcode OR set START pin high
  SPI.transfer(ADS_START);
  ////////////////////////////////////////
  // End SPI Setup
  ////////////////////////////////////////

  // This block parses incoming UDP packets for terminate command
  while(1)
  {
    noBytes = Udp.parsePacket();

    if ( noBytes ) {
      Udp.read(packetBuffer,noBytes);
      if (packetBuffer[0] == 't' || packetBuffer[1] == 't' || packetBuffer[2] == 't')
      {
        Serial.print("Packet Buffer: "); for (i=0; i < noBytes; i++) Serial.print(packetBuffer[i]);
        // TERMINATE STREAM
        Serial.println(" terminating stream");
        // Close SPI
        ADC_CloseSPI();
        return;
      }
    }

    //////////////////////////////////////////
    // Wait for DRDY LOW then Transfer data
    //////////////////////////////////////////

    // TODO Tie DRDY to transfer call, setup DRDY pin
    // while(digitalRead(DRDY_PIN) == HIGH); //TODO define DRDY PIN INPUT, is this every time or just first time?

    // Read 8 channels of data + status register
    for (i=0; i<26; i++) { // (3 byte sample * 8 channels) + 2 status reg
      sample_buffer[i] = SPI.transfer(0x00); // Could fold this straignt into Udp.write...
    }

    //////////////////////////////////////////
    // Send new samples over WiFi
    //////////////////////////////////////////

    // Stream ADS1299 Data
    Udp.beginPacket(host_ip,UDP_port);
    //TODO swap fake data for real
    // for (i=0; i<26; i++) Udp.write(sample_buffer[i]);
    Udp.write("Packet:                ");Udp.write(c);
    Udp.endPacket();

    // Log loop progress and delay
    if( (c%100) == 0 )Serial.print(".");
    if( (c%1000) == 0){Serial.print(c);Serial.println("");}
    c++;
    long int k = 0;
    for (k=0;k<UDP_Stream_Delay;k++) {
      if (k == 1000 && (c % 1000 == 0)) Serial.print("-");
    }
    // Note: tune less than value for tx throughput cap.
    //       k<1,000 yields about 6,000 sps
  }
}

void ADC_GetRegisterContents() {
  client.print("Here is your register contents.");
}

void ADC_SetUdpDelay() {
  UDP_Stream_Delay = (rx_buf_string.substring(rx_buf_string.indexOf("_b_")+3, rx_buf_string.indexOf("_e_"))).toInt();
  client.print("updating UDP delay");
  Serial.print("setting delay to: "); Serial.println(UDP_Stream_Delay);
}

void ADC_SetupSPI() {
  // Setup SPI
  SPI.begin();
  SPI.setDataMode(0);
  SPI.setFrequency(2000000);
  // NOTE eliminate pin manual pin usage for now
  // pinMode(15,OUTPUT); // Bit bang CS
  // digitalWrite(15,LOW); // Set CS Low for duration of serial comm
  // pinMode(DRDY_PIN, INPUT);
  // TODO may want to reset ADS (reset) or just SPI interface (CS)
}

void ADC_CloseSPI() {
  // Close ADS SPI Interface
  // TODO uncomment this: digitalWrite(15,HIGH);
  SPI.end();
}

void ADC_ReadRegisters() {

  // Setup SPI
  ADC_SetupSPI();

  // Stop read data continuous
  SPI.transfer(ADS_SDATAC);

  // Send RREG OpCodes
  SPI.transfer(ADS_RREG_1);
  SPI.transfer(ADS_RREG_2);

  // Populate AdsMap with responses
  int i;
  for(i=0; i<24; i++) {
    AdsMap[i] = SPI.transfer(0x00);
  }

  // Close SPI
  ADC_CloseSPI();

}

////////////////////////////////////////////////////////////////////////////////
// Power Management IC (BQ25120)
////////////////////////////////////////////////////////////////////////////////
void BQ_Setup() {

  // Initialize WIRE object
  Wire.begin();

  ////////////////////////////////////////////////////////////
  // IO15 == BQ_CD (i.e. chip enable/disable)
  pinMode(15,OUTPUT); // TODO shated with CS

  // If Vin is valid:
  //  HIGH = Disable charging
  //  LOW  = Enable charging

  // If Battery Only
  //  HIGH = Active battery management
  //  LOW  = High Z state

  // TODO track Vin in order to appropriately control BQ_CD

  ////////////////////////////////////////////////////////////
  // IO3 == BQ_INT (i.e. status/interrupt fault)
  pinMode(3,INPUT); // TODO shared with UART RX0

  // LOW == charging

  // High Z == charge complete or device disabled or Hi-Z mode

  // 128 uS interrupt pulse == fault occured

  attachInterrupt(3, BQ_handleFaultISR, RISING); //TODO ensure that interrupt can be attached to IO3!
  // Note: above interrupt can only be active when not using IO3 for UART mode

}

void BQ_handleFaultISR() {
  // TODO Read BQ over i2c for fault data - should not interrupt stream?
}

void BQ_readRegister(uint8_t reg_addr, int num_reg, uint8_t* BQ_Reg_Map) {
  ///////////////////////////////////////////////////////////////////////
  // Generic I2C read/write methods

  // Valid Register Addresses are 0x00 - 0x0B
  // Any attempt to read at another address will return 0xFF

  // Register contents can be found on page 35 of bq25120 datasheet

  // Generic BQ_I2C READ Method

  // Send BQ the address to begin reading from
  Wire.beginTransmission(BQ_8_ADDR);
  Wire.write(reg_addr);
  // Send repeated start command with slave addr but read bit set
  Wire.requestFrom(BQ_8_ADDR, num_reg);// could request more bits here...
  while (Wire.available()) {
    BQ_Reg_Map[num_reg++] = Wire.read();
  }
}

void BQ_writeRegister(uint8_t reg_addr, int num_reg, uint8_t* BQ_Set_Reg) {
  // Generic BQ_I2C WRITE Method

  // Send BQ the register begin writing at
  Wire.beginTransmission(BQ_8_ADDR);
  Wire.write(reg_addr);
  // Send num_reg reg values from BQ_Set_Req array
  int i;
  for (i = 0; i < num_reg; i++) Wire.write(BQ_Set_Reg[reg_addr + i]);
  Wire.endTransmission();
  // Note: clock stretching up to 100 uS is built into twi library
}
