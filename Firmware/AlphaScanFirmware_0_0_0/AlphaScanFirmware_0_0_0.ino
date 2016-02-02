#include <ESP8266WiFi.h>
#include <SPI.h>
#include <Wire.h>
#include <WiFiUDP.h>

// Define hard coded network constants
const char* ssid     = "PHSL2";
const char* password = "BSJKMVQ6LF2XH6BJ";
const char* host     = "192.168.1.8";

// TCP constants
const int   port     = 50007;

// UDP constants
const int   UDP_port = 2390;
byte packetBuffer[512]; //buffer to hold incoming and outgoing packets

// Declare WiFi client 
WiFiClient client;

// Declare Udp Instance
WiFiUDP Udp;

// Declare function prototypes
void establishHostTCPConn();
void ADC_StartDataStream();
void ADC_getRegisterContents();

void setup() {
  // Setup Serial
  Serial.begin(115200);
  // Setup I2C
  // Setup SPI
  // Setup WiFi

  //--Connect to host application--//

  // 1) Use a) hard-coded, b) stored, c) serial uploaded SSID and Passkey to connect (see: https://github.com/esp8266/Arduino/blob/master/doc/filesystem.md)
  // TODO Establish communication loop with host over serial w/ 115200 Baudrate
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP()); 

  // Bind local Wifi port
  Udp.begin(UDP_port);
}

void loop() {
  // If not connected, connect to host (could potentially do this check via an exception on trying to client.print())
  if (!client.status()) establishHostTCPConn();
 
  // Check for command from Host
  String line = client.readStringUntil('\r');

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
      client.print("Here is your accelerometer data");
      break;

    case 'p': //read pwr data
      client.print("Here is your power data");
      break;
      
    case 'i': //information request
      client.print("Dear host, here is your information");
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

//////////////////////////////////////////////////////////////////////////////////////////
//////////////////////Utility Methods/////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////

void establishHostTCPConn() {
  

  Serial.println("Attempting to connect to host");
  
  // Connet to host
  while (!client.connect(host,port)); //TODO turn this into do while loop to see if serial prints at the right time
  {
    Serial.println("Connection failed");
    Serial.println("wait 1 sec...");
    delay(1000);    

    // TODO Account for various exceptions here...

    // TODO After a limited number of attempts, recheck wifi connection
    
  }
  client.print("Connected");
  Serial.println("Connected to host");
}

//ADS1299 Spi Controll////////////////////////////////////////////////////////////////////
// TODO create ADS1299 class to track register contents and device status
void ADC_SetupDefaultConfig() {
  
}

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
        // TODO run termination ACK protocol here so that log thread on host exits properly 
        Serial.println("terminating stream");
        return;
      } 
    }

    // Transf
    
    // Stream ADS1299 Data
    Udp.beginPacket(host,UDP_port);
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

void ADC_getRegisterContents() {
  
}
//Power Management Control////////////////////////////////////////////////////////////////
// TODO create pwr_man class to track status

//Accelerometer Control///////////////////////////////////////////////////////////////////
// TODO create accel class to track status











