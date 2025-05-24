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

// Standard Address for the MPU is 0x68
MPU6050 mpu;

// Defining the size/range that we will later map compass calculations to
#define SENSOR_RANGE 1024



// Setting up the 16-bit integers to hold the compass heading in 3 axis. 
int16_t vx, vy, vz;
// Prepairing the variables that the calibration numbers go into
int16_t cal_min_x, cal_min_y, cal_max_x, cal_max_y;
short cal_offset_x, cal_offset_y, cal_range_x, cal_range_y;
short calibrated_x, calibrated_y;

// Float for keeping track of the heading in degress
float c_heading;



void setup()
{

  // Calibration-values from "Compass_Calibration.ino"
  cal_min_x = -168;
  cal_max_x = 119;
  cal_min_y = -46;
  cal_max_y = 245;


  //Precalculating the offsets on x and y for the compass.
  cal_offset_x = (short)(((long)cal_max_x + (long)cal_min_x) / 2);
  cal_range_x = cal_max_x - cal_offset_x;
  cal_offset_y =(short)(((long)cal_max_y + (long)cal_min_y) / 2);
  cal_range_y = cal_max_y - cal_offset_y;


  // Opening I2C connection 
  Wire.begin();
  
  // Starting serial communication with computer
  Serial.begin(9600);  
  Serial.println("Wire connection and Serial connection started....");

  //Initializing the MPU in order to enable the I2C bypass
  mpu.initialize();
  mpu.setI2CBypassEnabled(true);
  
  // When I2C bypass is enabled on the MPU we can then initialize the compass
  comp.initialize();

  Serial.println(comp.testConnection());
  
}

void loop()
{
  //Defining the memory address of the variables
  //So that they can be changed at once. Instead of running the 
  //getHeading 3 times.
  comp.getHeading(&vx, &vy, &vz);

  
  //Calculate the calibrated values for the atan2 calculation below
  calibrated_x = (short)(((long)(vx - cal_offset_x) * (long)SENSOR_RANGE) / (long)cal_range_x);
  calibrated_y = (short)(((long)(vy - cal_offset_y) * (long)SENSOR_RANGE) / (long)cal_range_y);  

  // Calculation to go from vectors in getHeading to degrees 
  c_heading = 180 - atan2((double)calibrated_y, (double)calibrated_x) * 180.0/3.14159265;

  Serial.print(c_heading);
  Serial.println("°");

  // Works best if running about 10 times pr second.
  delay(100);
  
}
