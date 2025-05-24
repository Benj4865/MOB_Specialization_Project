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
AK8975 comp(0x0c);

// Address for the MPU is 0x68
MPU6050 mpu;

// Setting up the 16-bit integers to hold the compass heading in 3 axis. 
int16_t vx, vy, vz;
float c_heading;

void setup()
{

  // Opening I2C connection 
  Wire.begin();
  
  // Starting serial communication with computer
  Serial.begin(9600);

  
  Serial.println("Wire connection and Serial connection started....");

  mpu.initialize();
  mpu.setI2CBypassEnabled(true);
  comp.initialize();

  Serial.println(comp.testConnection());
  
}

void loop()
{

  //Defining the memory address of the variables
  //So that they can be changed at once. Instead of running the 
  //getHeading 3 times.
  comp.getHeading(&vx, &vy, &vz);

  // Calculation to go from vectors in getHeading to degrees 
  c_heading = atan2((double)vy, (double)vx) * 180.0/3.14159265 + 180;
  while (c_heading < 0) c_heading += 360;
  while (c_heading > 360) c_heading -= 360;

  Serial.print(c_heading);
  Serial.println("°");

  // Works best if running about 10 times pr second.
  delay(100);
  
}
