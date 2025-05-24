// Some of the code in this script is inspired by the way communication is handled in the
// Example files in the libraries. No AI has been used for creating this code


// Using a custom libraries made by jrowberg on github that handles the "virtual" I2C communication to the compass and MPU chip
// Libraries: https://github.com/jrowberg/i2cdevlib/tree/master
#include  "I2Cdev.h"
#include "AK8975.h"
#include "MPU6050.h"

// Arduino library that handles the hardware I2C single-wire connections.
#include "Wire.h"

// Standard address for the compass is 0x0c so we will define it here.
AK8975 mag(0x0c);

// Address for the MPU is 0x68
MPU6050 mpu;

// Setting up the variable to hold the compass heading in 3 axis. 
int16_t mx, my, mz;
float c_heading;

void setup() {

  
  Wire.begin();
  

}

void loop() {
  // put your main code here, to run repeatedly:

}
