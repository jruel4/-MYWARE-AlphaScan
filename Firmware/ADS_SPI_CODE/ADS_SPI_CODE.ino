
// the sensor communicates using SPI, so include the library:
#include <SPI.h>

void setup() {
  Serial.begin(115200);
}

void loop() {

}

//////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////

// ADS1299 SPI OPCODES
const uint8_t ADS_WAKEUP = (0x02); //wakeup
const uint8_t ADS_STANDBY = (0x04); //standby
const uint8_t ADS_RESET = (0x06); //reset
const uint8_t ADS_START  = (0x08); //start
const uint8_t ADS_STOP = (0x0A); //stop
const uint8_t ADS_RDATAC = (0x10); //read data continuous
const uint8_t ADS_SDATAC = (0x11); //stop read data continuous
const uint8_t ADS_RDATA = (0x12); //read data by command
const uint8_t ADS_RREG_1 = (0x20); //read reg start at register 0
const uint8_t ADS_RREG_2 = (0x17); //read all 24 register(s)
const uint8_t ADS_WREG_1 = (0x40); //write registers starting at 0
const uint8_t ADS_WREG_2 = (0x00); //write one register

uint8_t AdsMap[24] = {0}; //map of ADS registers

// Setup ADS SPI Interface
void ADC_SetupSPI() {
  // Setup SPI
  SPI.begin();
  SPI.setDataMode(0);
  SPI.setFrequency(2000000);
  pinMode(15,OUTPUT); // Bit bang CS
  digitalWrite(15,LOW); // Set CS Low for duration of serial comm
  // TODO may want to reset ADS (reset) or just SPI interface (CS)
}

// Close down ADS SPI Interface
void ADC_CloseSPI() {
  // Close ADS SPI Interface
  digitalWrite(15,HIGH);
  SPI.end();
}

// Read all registers
void ADC_readRegisters() {

  // Setup SPI
  ADC_SetupSPI();
  
  // Stop read data continuous
  SPI.transfer(SDATAC);

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

void ADC_beginStream() {

  // Setup SPI
  ADC_SetupSPI();

  //////////////////////////////////////////
  //Add to beginning of ADC_StartStream()///
  //////////////////////////////////////////
  int i;
  uint8_t sample_buffer[26];
  // Start read data continuous
  SPI.transfer(ADS_RDATAC);

  // Send start opcode OR set START pin high
  SPI.transfer(ADS_START);
  //////////////////////////////////////////
  //////////////////////////////////////////


  //////////////////////////////////////////
  //Add to 'Transfer Latest Sample' Section/
  //////////////////////////////////////////

  // TODO Tie DRDY to transfer call, setup DRDY pin
  while(digitalRead(DRDY_PIN) == HIGH);

  // Read 8 channels of data + status register
  
  for (i=0; i<26; i++) { // (3 byte sample * 8 channels) + 2 status reg
    sample_buffer[i] = SPI.transfer(0x00);
  }

  //////////////////////////////////////////
  //////////////////////////////////////////
  
  //////////////////////////////////////////
  //Add to end to 'Terminate Stream' Section
  //////////////////////////////////////////
  // Close SPI
  ADC_CloseSPI();
  
}





