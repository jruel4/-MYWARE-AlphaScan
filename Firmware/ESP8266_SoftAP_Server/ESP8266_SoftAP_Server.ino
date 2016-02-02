#include <ESP8266WiFi.h>

//////////////////////
// WiFi Definitions //
//////////////////////

const char AP_NAME_STR[] = "AlphaScanAP";
const char WiFiAPPSK[] = "martianwearables";
String custom_response;
long int c = 0;
WiFiServer server(80);

void setup() 
{
  Serial.begin(115200);
  WiFi.mode(WIFI_AP); // MAIN CALL TO SET WIFI MODE
  WiFi.softAP(AP_NAME_STR, WiFiAPPSK); // THIS IS THE MAIN CALL TO SETUP AP
  server.begin();
  Serial.println("WiFi configured");
}

void loop() 
{
  /////////////////////////////////////////////////////////////////////////////////
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    if(c++ % 1000000 == 0)Serial.print(".");if(c % 10000000 ==0)Serial.println("");
    return;
  }

  /////////////////////////////////////////////////////////////////////////////////
  // Read the first line of the request
  String req = client.readStringUntil('\r');
  Serial.print("Request received: ");Serial.print(req);Serial.println("");
  client.flush();

  /////////////////////////////////////////////////////////////////////////////////
  // Parse request

  // Alive request
  if (req.indexOf("alive") >= 0) {
    custom_response = "___IAMALPHASCAN___";
  }

  
  // Rx SSID
  else if (req.indexOf("ssid") >= 0) {
    custom_response = "SSID";
  }

  // Rx passkey
  else if (req.indexOf("pass") >= 0) {
    custom_response = "passkey";
  }

  // Rx Host IP
  else if (req.indexOf("host_ip") >= 0) {
    custom_response = "Host IP";
  }

  // Echo network params
  else if (req.indexOf("echo_params") >= 0) {
    custom_response = "network params";
  }

  else {
    custom_response = "unknown_request";
  }

  /////////////////////////////////////////////////////////////////////////////////
  // Prepare the response. Start with the common header:
  String s = "HTTP/1.1 200 OK\r\n";
  s += "Content-Type: text/html\r\n\r\n";
  s += "<!DOCTYPE HTML>\r\n<html>\r\n";
  /////////////////////////////////////////////////////////////////////
  // If we're setting the LED, print out a message saying we did
  s += custom_response;
  /////////////////////////////////////////////////////////////////////
  s += "</html>\n";

  // Send the response to the client
  client.print(s);
  delay(1);
  Serial.println("Client disonnected");

  // The client will actually be disconnected 
  // when the function returns and 'client' object is detroyed
}


