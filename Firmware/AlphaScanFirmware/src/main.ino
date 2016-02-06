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

////////////////////////////////////////////////////////////////////////////////
// Global variables
////////////////////////////////////////////////////////////////////////////////
char ssid[20];                          //
char password[50];                      //
char host_ip[15];                       //

String ssid_str;                        //
String password_str;                    //
String host_ip_str;                     //

bool ssid_set     = false;              //
bool password_set = false;              //
bool host_ip_set  = true;               //
bool network_set  = false;              //

const int TCP_port = 50007;             //
const int UDP_port = 2390;              //
                                        //
byte packetBuffer[512];                 //
WiFiClient client;                      //
WiFiUDP Udp;                            //

bool open_a = true;                     //
File f;                                 //
const char path[] = "/neti_params.txt"; //
String firmware_version = "0.0.3";      //

enum T_SYSTEM_STATE {
  AP_MODE,
  RUN_MODE
} SYSTEM_STATE;

////////////////////////////////////////////////////////////////////////////////
// Function prototype declarations
////////////////////////////////////////////////////////////////////////////////
void establishHostTCPConn();
void ADC_StartDataStream();
void ADC_getRegisterContents();
void processClientRequest();
void acquireNetworkParams();
String extractValue(String,String);
void readSpiffsForParams();
void readApForParams();
void connectToWan();
void handleOTA();
void setupOTA();
void generalSetup();

////////////////////////////////////////////////////////////////////////////////
// Function definitions
////////////////////////////////////////////////////////////////////////////////
void setup() {

  generalSetup();
  readSpiffsForParams();
  readApForParams();
  connectToWan();
}

void loop() {

  switch (SYSTEM_STATE) {
    case AP_MODE:
    {
      readApForParams();
      connectToWan();
      break;
    }
    case RUN_MODE:
    {
      establishHostTCPConn();
      processClientRequest();
      break;
    }
    default:
    {
      Serial.println("Invalid SYSTEM_STATE");
      break;
    }
  }

}

void generalSetup() {

  Serial.begin(74880);
  Serial.println("");
  Serial.println("Firmware version: "+firmware_version);
}

void connectToWan() {

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
  Serial.println(WiFi.localIP());

  Udp.begin(UDP_port);

  SYSTEM_STATE = RUN_MODE;
}

void readApForParams() {

  // acquire SSID and password via SoftAP
  Serial.println("acquire SSID and other network params now...");
  while(!network_set) {

    acquireNetworkParams();

    if (network_set) {
      // Write network params to SPIFFS

      // open file
      f = SPIFFS.open(path,"w");
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

void readSpiffsForParams() {
  /////////////////////////////////////////////////////////////////////////////////////////////////////
  // Check SPIFFS for network parameters
  /////////////////////////////////////////////////////////////////////////////////////////////////////

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
      ssid_str = extractValue(ssid_str,"ssid");
      strcpy(ssid,&(ssid_str[0]));
      ssid_set = true;

      Serial.print("RS_SSID: ");Serial.println(ssid);
    }

    // Read password
    if(f.available()) {
      //Lets read line by line from the file
      password_str = f.readStringUntil('\n');
      password_str = extractValue(password_str,"pass");
      strcpy(password,&(password_str[0]));
      password_set = true;

      Serial.print("RS_PASS: ");Serial.println(password);
    }

    // Read host_ip
    if(f.available()) {
      //Lets read line by line from the file
      host_ip_str = f.readStringUntil('\n');
      host_ip_str = extractValue(host_ip_str,"host_ip");
      strcpy(host_ip,&(host_ip_str[0]));
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

void acquireNetworkParams() {

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
    client.print("HTTP/1.1 200 OK\r\nfuck off");
    delay(1);
    client.stop();
    delay(1);
    return;
  }

  // Read the first line of the request
  String req = client.readStringUntil('\r');
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

  // Rx passkey
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


  // Send the response to the client
  String s = "HTTP/1.1 200 OK\r\n";
  s += "Content-Type: text/html\r\n\r\n";
  s += "<!DOCTYPE HTML>\r\n<html>\r\n";
  s += custom_response;
  s += "</html>\n";
  client.print(s);
  delay(1);
  Serial.println("Client disonnected");

}

void processClientRequest() {

  // Check for command from Host
  String line = client.readStringUntil('\r');

  // Switch between possible command cases
  if (line.length() == 0) return;
  switch(line[0]) {

    ////////////////////////////////////////////////////////////////////////////
    case 's': //start streaming adc data
    {
      ADC_StartDataStream();
      break;
    }

    ////////////////////////////////////////////////////////////////////////////
    case 'r': // get ADS1299 registers
    {
      ADC_getRegisterContents();
      break;
    }

    ////////////////////////////////////////////////////////////////////////////
    case 't': //stop streaming adc data
    {
      // this command does nothing in this context
      break;
    }

    ////////////////////////////////////////////////////////////////////////////
    case 'a': //read accelerometer data
    {
      client.print("Here is your accelerometer data");
      break;
    }

    ////////////////////////////////////////////////////////////////////////////
    case 'p': //read pwr data
    {
      client.print("Here is your power data");
      break;
    }

    ////////////////////////////////////////////////////////////////////////////
    case 'i': //information request
    {
      client.print("Dear host, here is your information");
      break;
    }

    ////////////////////////////////////////////////////////////////////////////
    case 'u': //update register contents
    {
      Serial.println("Received request to update ADC registers");
      Serial.println(line);
      break;
    }

    ////////////////////////////////////////////////////////////////////////////
    case 'o': //OTA update
    {
      handleOTA();
      break;
    }

    ////////////////////////////////////////////////////////////////////////////
    case 'q': //AP mode
    {
      client.stop();
      delay(1);
      Serial.println("Forcing AP Mode");
      SYSTEM_STATE = AP_MODE;
      network_set = host_ip_set = ssid_set = password_set = false;
      break;
    }

    ////////////////////////////////////////////////////////////////////////////
    default:
    {
      Serial.print(".");
      break;
    }

  }
}

void setupOTA() {
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

void handleOTA() {
  // handle ota
  Serial.println("handing OTA - must either update or reset device");
  // shutdown previous tcp connections
  client.stop();
  delay(100);
  //
  setupOTA();
  while(1) {
    ArduinoOTA.handle();
    delay(1);
  }
}

void establishHostTCPConn() {

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
      Udp.read(packetBuffer,noBytes);
      if (packetBuffer[0] == 't' || packetBuffer[1] == 't' || packetBuffer[2] == 't')
      {
        // TERMINATE STREAM
        Serial.println("terminating stream");
        return;
      }
    }

    // Stream ADS1299 Data
    Udp.beginPacket(host_ip,UDP_port);
    Udp.write("Packet:                ");Udp.write(c);
    Udp.endPacket();

    // Log loop progress and delay
    if( (c%100) == 0 )Serial.print(".");
    if( (c%1000) == 0){Serial.print(c);Serial.println("");}
    c++;
    int k = 0;
    for (k=0;k<1000;k++);
    // Note: tune less than value for tx throughput cap.
    //       k<1,000 yields about 6,000 sps

  }
}

void ADC_getRegisterContents() {}

String extractValue(String Request, String delimeter) {
  // Standard request syntax is "delimeter_value_enddelimeter"
  // This method extracts "value"
  return Request.substring( (Request.indexOf(delimeter) + delimeter.length() + 1), Request.indexOf("end"+delimeter) - 1);
}
