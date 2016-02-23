


// Read all registers


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
  while(digitalRead(DRDY_PIN) == HIGH); //TODO define DRDY PIN INPUT

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
