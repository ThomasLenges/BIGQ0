#include <Wire.h>

void setup() {
  // Initialize the I2C communication
  Wire.begin();
  //Wire1.begin(); // I2C in Qwiic connector
}

void loop() {
  // Replace with the target device’s I2C address
  byte deviceAddress = 0x35;
  // Replace with the appropriate instruction byte
  byte instruction = 0x00; // RnW
  // Replace with the value to send
  byte value = 0xFA;
  // Begin transmission to the target device
  Wire.beginTransmission(deviceAddress);
  // Send the instruction byte
  Wire.write(instruction);
  // Send the value
  Wire.write(value);
  // End transmission
  Wire.endTransmission();

  delay(2000);
}