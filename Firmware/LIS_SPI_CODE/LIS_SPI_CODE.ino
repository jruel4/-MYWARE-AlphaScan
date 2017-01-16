#include <SPI.h>
#include <map>

void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

}

// TODO Define interrupts 1 and 2 

// LIS INT1 == IO4
pinMode(4,INPUT);
attachInterrupt(4, LIS_Int1Isr ,RISING); //TODO confirm rising

// LIS INT2 == IO0
pinMode(0, INPUT);
attachInterrupt(0, LIS_Int2Isr, RISING); 


// Define variables
std::map<uint8_t,uint8_t> LIS_REG_MAP[38];
std::map<uint8_t,uint8_t> LIS_SET_REG[38];
// TODO: add comments to valid registers
uint8_t LIS_ValidReadRegsiters[38] = {
  0x0B,
  0x0C,
  0x0E,
  0x0F,
  0x1E,
  0x1F,
  0x20,
  0x21,
  0x22,
  0x23,
  0x24,
  0x25,
  0x26,
  0x27,
  0x28,
  0x29,
  0x2A,
  0x2B,
  0x2C,
  0x2D,
  0x2E,
  0x2F,
  0x30,
  0x31,
  0x32,
  0x33,
  0x34,
  0x35,
  0x36,
  0x37,
  0x38,
  0x39,
  0x3A,
  0x3B,
  0x3C,
  0x3D,
  0x3E,
  0x3F
}

uint8_t LIS_ValidWriteRegisters[24] = {
  0x1E,
  0x1F,
  0x20,
  0x21,
  0x22,
  0x23,
  0x24,
  0x25,
  0x26,
  0x2E,
  0x30,
  0x32,
  0x33,
  0x34,
  0x35,
  0x36,
  0x38,
  0x39,
  0x3A,
  0x3B,
  0x3C,
  0x3D,
  0x3E,
  0x3F
}

uint8_t LIS_Read_Bit = 0x01;
uint8_t LIS_Write_Bit = 0x00;

// Read Registers
void LIS_ReadRegisters() {
  // Initialize SPI and set LIS CS low
  SPI.begin();
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);

  // TODO: ensure that IF_ADD_INC == 1

  // Send address and R/W bit
  SPI.transfer(LIS_ValidReadRegsiters[0] | LIS_Read_Bit);

  // Issue read commands and populate LIS_REG_MAP
  int i;
  for (i=0; i<38; i++) LIS_REG_MAP[LIS_ValidReadRegsiters[i]] = SPI.transfer(0x00);

  // Close spi and deselect LIS CS
  digitalWrite(5, HIGH);
  SPI.close();
}

// Write Registers
void LIS_WriteRegister(uint8_t reg_addr, uint8_t reg_val) {
  // Initialize SPI and set LIS CS low
  SPI.begin();
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);

  // Send address and R/W bit
  SPI.transfer(reg_addr | LIS_Write_Bit);

  // Send value to place in address
  SPI.transfer(reg_val);

  // Close spi and deselect LIS CS
  digitalWrite(5, HIGH);
  SPI.close();
}

void LIS_WriteRegistersAll() {
  // Initialize SPI and set LIS CS low
  SPI.begin();
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);

  // TODO ensure auto-increment / DOES IF_AUTO_INC only go to R/W register?

  // Send start address and R/W Bit
  SPI.transfer(LIS_ValidWriteRegisters[0] | LIS_Write_Bit);

  // Transfer register contents to write
  int i;
  for (i=0; i<24; i++) SPI.transfer(LIS_SET_REG[LIS_ValidWriteRegisters[i]]); // Note: auto-inc may not work as expected here

  // Close spi and deselect LIS CS
  digitalWrite(5, HIGH);
  SPI.close();
}

// Check Reg Map Validity
void LIS_CheckMapValidity() {
  // TODO Compare Read Map to Write Map
  // Note some write register are command and immediatly change, so only check certain static settings
}

// LIS_Int1Isr
void LIS_Int1Isr() {
  //TODO
}

// LIS_Int2Isr
void LIS_Int1Isr() {
  //TODO
}

