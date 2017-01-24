#include <Wire.h>

// Constants
const uint8_t BQ_7_ADDR = 0x6A; // (0xD4 - 8 bit shifted)
const uint8_t BQ_8_ADDR = 0xD4;

uint8_t BQ_Reg_Map[12];
uint8_t BQ_Set_Reg[12];

void setup() {

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

void loop() {
  // put your main code here, to run repeatedly:

}


// TODO Read BQ over i2c for fault data - should not interrupt stream?
void BQ_handleFaultISR() {

}

///////////////////////////////////////////////////////////////////////
// Generic I2C read/write methods

// Valid Register Addresses are 0x00 - 0x0B
// Any attempt to read at another address will return 0xFF

// Register contents can be found on page 35 of bq25120 datasheet

// Generic BQ_I2C READ Method
void BQ_readRegister(uint8_t reg_addr, int num_reg, uint8_t* BQ_Reg_Map) {

  // Send BQ the address to begin reading from
  Wire.beginTransmission(BQ_8_ADDR);
  Wire.write(reg_addr);
  // Send repeated start command with slave addr but read bit set
  Wire.requestFrom(BQ_8_ADDR, num_reg);// could request more bits here...
  while (Wire.available()) {
    BQ_Reg_Map[num_reg++] = Wire.read();
  }
}

// Generic BQ_I2C WRITE Method
void BQ_writeRegister(uint8_t reg_addr, int num_reg, uint8_t* BQ_Set_Reg) {

  // Send BQ the register begin writing at
  Wire.beginTransmission(BQ_8_ADDR);
  Wire.write(reg_addr);
  // Send num_reg reg values from BQ_Set_Req array
  int i;
  for (i = 0; i < num_reg; i++) Wire.write(BQ_Set_Req[reg_addr + i]);
  Wire.endTransmission();
  // Note: clock stretching up to 100 uS is built into twi library
}
