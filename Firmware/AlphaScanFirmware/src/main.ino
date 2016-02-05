////////////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////////////
#include <ArduinoOTA.h>     // Over the Air updates
#include <ESP8266WiFi.h>    // WiFi Class
#include <ESP8266mDNS.h>    // DNS Class
#include <SPI.h>            // Serial Peripheral Interface
#include <Wire.h>           // Inter-Integrated Circuit
#include <WiFiUDP.h>        // UDP
#include "FS.h"             // File system (SPIFFS)

////////////////////////////////////////////////////////////////////////////////
// Declare global variables
////////////////////////////////////////////////////////////////////////////////
char host_ip[20];           // TODO eliminate this by retreiving over UDP listener then: strcpy(host,&(host_str[0]));
char ssid[20];              // WAN Router SSID
char password[50];          // WAN Router password

String host_ip_str;         // Stores host_ip for convinient manipulation
String ssid_str;            // Stores ssid for convinient manipulation
String password_str;        // Stores password for convinient manipulation

bool ssid_set     = false;  // ssid has been acquired
bool password_set = false;  // password has been acquired
bool host_ip_set     = true;   // host_ip has been acquired
bool network_set  = false;  // all network params have been acquired

const int TCP_port = 50007; // Port number opened by TCP host
const int UDP_port = 2390;  // Port number used for both ends of UDP stream

byte UDP_packetBuffer[512]; // Buffer to hold incoming and outgoing packets

WiFiClient AP_client;       // Access Point client object
WiFiClient TCP_client;      // Main TCP control client object
WiFiUDP    Udp;             // UDP object for streaming ADS data

const char path[] = "/net_params.txt";

////////////////////////////////////////////////////////////////////////////////
// Declare function prototypes
////////////////////////////////////////////////////////////////////////////////
void establishHostTCPConn();
void ADC_StartDataStream();
void ADC_getRegisterContents();
void processClientRequest();
void acquireNetworkParams();
void acquireNetworkParams_SPIFFS();
void acquireNetworkParams_AP();
void connectToWAN();
String extractValue(String,String);

////////////////////////////////////////////////////////////////////////////////
// Function definitions
////////////////////////////////////////////////////////////////////////////////
void setup() {

  Serial.begin(74880);
  acquireNetworkParams();
  connectToWAN();
}

void loop() {
  // If not connected, connect to host (could potentially do this check via an exception on trying to client.print())
  establishHostTCPConn();

  // Read and parse client message
  processClientRequest();

}

void acquireNetworkParams() {

  acquireNetworkParams_SPIFFS();

  // If failed to retrieve params from SPIFFS, start SoftAP
  while(!network_set) {

    acquireNetworkParams_AP();

    if (network_set) {
      // Write network params to SPIFFS

      // open file
      File f = SPIFFS.open(path,"w");
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
      f.close();
    }
  }

  Serial.println("Network parameters acquired.");
  Serial.println("ssid: " + ssid_str + ", pass: " + password_str );
}

void connectToWAN() {
  //WiFi.begin("PHSL2", "BSJKMVQ6LF2XH6BJ");
  WiFi.begin(ssid, password);

  // TODO add counter here, and if does not work after N tries, switch to SoftAP state. Requires state machine
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempts++;

    if (attempts > 15) { // may want to tune this number up for poor connections
      Serial.println("WiFi parameters appear to be invalid");
    }
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  Udp.begin(UDP_port);
}

void acquireNetworkParams_SPIFFS() {

  /////////////////////////////////////////////////////////////////////////////////////////////////////
  // Check SPIFFS for network parameters
  /////////////////////////////////////////////////////////////////////////////////////////////////////

  // Declare filesystem variables
  bool open_a = true;
  File f;

  // Initiate SPIFFS
  Serial.println("inititating file SPIFFS class");
  if(SPIFFS.begin())Serial.println("Spiffs mount success");else {Serial.println("Spiffs mount FAIL");return;}

  // Check to see if net_params file exists
  Serial.print("checking if exists: ");Serial.println(path);
  if(SPIFFS.exists(path)) {
    Serial.println("path exists");
    open_a = true;
  }
  else {
    Serial.println("path does not exist");
    open_a = false;
  }

  // If path exists, try to open file
  if (open_a) {
    f = SPIFFS.open(path,"r");

    // Check if file open succeeded
    if (!f) {
      Serial.println("file open failed");
      return; // TODO deal with this properly...
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
      ssid_str = extractValue(ssid_str,"ssid");
      strcpy(ssid,&(ssid_str[0]));
      ssid_set = true;
    }

    // Read password
    if(f.available()) {
      //Lets read line by line from the file
      password_str = f.readStringUntil('\n');
      password_str = extractValue(password_str,"pass");
      strcpy(password,&(password_str[0]));
      password_set = true;
    }

    f.close();

    network_set = true;

  }
  // else procees to SoftAP Mode
  else {
    network_set = false;
  }
}

void acquireNetworkParams_AP() {

  // Define local AP variables
  const char AP_NAME_STR[] = "AlphaScanAP";
  const char WiFiAPPSK[] = "martianwearables";
  String custom_response;
  long int c = 0;
  int i;
  WiFiServer server(80);

  // Setup software access point (SoftAP)
  WiFi.mode(WIFI_AP); // MAIN CALL TO SET WIFI MODE
  WiFi.softAP(AP_NAME_STR, WiFiAPPSK); // THIS IS THE MAIN CALL TO SETUP AP
  server.begin();

  // Loop and listen for client data
  /////////////////////////////////////////////////////////////////////////////////
  // Check if a client has connected



  AP_client = server.available();
  while (!AP_client) {
    AP_client = server.available();
    if(c++ % 10000000 == 0)Serial.print(".");if(c % 100000000 ==0)Serial.println("");
  }

  if (ssid_set && host_ip_set && password_set) {
    network_set = true;
    Serial.println("Network is set");
    delay(1);
    AP_client.print("HTTP/1.1 200 OK\r\nfuck off");
    delay(1);
    AP_client.stop();
    delay(1);
    return;
  }


  /////////////////////////////////////////////////////////////////////////////////
  // Read the first line of the request
  String req = AP_client.readStringUntil('\r');
  Serial.print("Request received: ");Serial.print(req);Serial.println("");
  AP_client.flush();

  /////////////////////////////////////////////////////////////////////////////////
  // Parse request

  // Alive request
  if (req.indexOf("alive") >= 0) {
    custom_response = "___IAMALPHASCAN___";
  }

  // Rx SSID
  else if (req.indexOf("ssid") >= 0) {
    // collect SSID into local variables
    ssid_str = extractValue(req,"ssid");
    strcpy(ssid,&(ssid_str[0]));
    custom_response = "SSID";
    ssid_set = true;

    Serial.print("received ssid: ");Serial.println(ssid);
  }

  // Rx passkey
  else if (req.indexOf("pass") >= 0) {
    password_str = extractValue(req,"pass");
    strcpy(password,&(password_str[0]));
    custom_response = "passkey";
    password_set = true;

    Serial.print("received pass: ");Serial.println(password);
  }

  // host_ip passkey
  else if (req.indexOf("host_ip") >= 0) {
    host_ip_str = extractValue(req,"host_ip");
    strcpy(host_ip,&(host_ip_str[0]));
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


  // Send the response to the AP_client
  String s = "HTTP/1.1 200 OK\r\n";
  s += "Content-Type: text/html\r\n\r\n";
  s += "<!DOCTYPE HTML>\r\n<html>\r\n";
  s += custom_response;
  s += "</html>\n";
  AP_client.print(s);
  delay(1);
  Serial.println("AP_client disonnected");

  // close softAP to allow regular wifi connection?
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(1000);

}

void establishHostTCPConn() {

  if (!TCP_client.status()) {

    Serial.println("Attempting to connect to host");

    // Connet to host
    while (!TCP_client.connect(host_ip,TCP_port)); //TODO turn this into do while loop to see if serial prints at the right time
    {
      Serial.println("Connection failed");
      Serial.println("wait 1 sec...");
      delay(1000);

      // TODO Account for various exceptions here...

      // TODO After a limited number of attempts, recheck wifi connection

    }
    TCP_client.print("Connected");
    Serial.println("Connected to host");
  }
}

void processClientRequest() {

  // Check for command from Host
  String line = TCP_client.readStringUntil('\r');

  // Switch between possible command cases
  if (line.length() == 0) return;
  switch(line[0]) {

    case 's': //start streaming adc data
    ADC_StartDataStream();
    break;

    case 'r': // get ADS1299 registers
    ADC_getRegisterContents();
    break;

    case 't': //stop streaming adc data
    // this command does nothing in this context
    break;

    case 'a': //read accelerometer data
    TCP_client.print("Here is your accelerometer data");
    break;

    case 'p': //read pwr data
    TCP_client.print("Here is your power data");
    break;

    case 'i': //information request
    TCP_client.print("Dear host, here is your information");
    break;

    case 'u': //update register contents
    // TODO go unto sub-switch here for devices other than adc
    Serial.println("Received request to update ADC registers");
    Serial.println(line);
    break;

    default:
    Serial.print(".");
    break;

  }
}

void ADC_SetupDefaultConfig() {}

void ADC_StartDataStream() {

  Serial.println("Initiating stream");

  // Define constants
  int noBytes = 0;
  uint32_t c  = 0;



  while(1)
  {
    noBytes = Udp.parsePacket();

    if ( noBytes ) {
      Udp.read(UDP_packetBuffer,noBytes);
      if (UDP_packetBuffer[0] == 't' || UDP_packetBuffer[1] == 't' || UDP_packetBuffer[2] == 't')
      {
        // TERMINATE STREAM
        // TODO run termination ACK protocol here so that log thread on host exits properly
        Serial.println("terminating stream");
        return;
      }
    }

    // Transf

    // Stream ADS1299 Data
    Udp.beginPacket(host_ip,UDP_port);
    Udp.write("Packet:                ");Udp.write(c); // TODO fill this up with 26 bytes of 'sample_buffer'
    Udp.endPacket();

    // Log loop progress and delay
    if( (c%100) == 0 )Serial.print(".");
    if( (c%1000) == 0){Serial.print(c);Serial.println("");}
    c++;
    //delayMicroseconds(2000); // TODO find working microsecond delay to increase throughput beyond 1ksps
    delay(1);

    // TODO periodically run ALIVE() protocol to guard against sending to nobody
  }
}

void ADC_getRegisterContents() {}

String extractValue(String Request, String delimeter) {
  // Standard request syntax is "delimeter_value_enddelimeter"
  // This method extracts "value"
  return Request.substring( (Request.indexOf(delimeter) + delimeter.length() + 1), Request.indexOf("end"+delimeter) - 1);
}

////////////////////////////////////////////////////////////////////////////////
// Misc TODO's
////////////////////////////////////////////////////////////////////////////////
// TODO create pwr_man class to track status
// TODO create ADS1299 class to track register contents and device status
// TODO create accel class to track status
