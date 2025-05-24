// Some of the code in this script is inspired by the way communication is handled in the
// Example files in the libraries. No AI has been used for creating this code

// Arduino library that handles the hardware I2C single-wire connections.
#include "Wire.h"

// Using a custom libraries made by jrowberg on github that handles the "virtual" I2C communication to the compass and MPU chip
// Libraries: https://github.com/jrowberg/i2cdevlib/tree/master
#include "I2Cdev.h"
#include "MPU6050.h"
#include "AK8975.h"

// Standard IC2 address for gyro MPU60509 is (0x68)

MPU6050 mpu;

// Standard address for the compass is 0x0c so we will define it here.
AK8975 comp;

int16_t mx, my, mz;
int16_t min_x, min_y, min_z, max_x, max_y, max_z;

void setup() {

    // random values that has to be bigger and smaller than anything that the sensor can output.
    min_x, min_y, min_z = 1000;
    max_x, max_y, max_z = -1000;

    // Opening the I2C connection
    Wire.begin();

    // Starting serial communication with computer
    Serial.begin(9600);

    
    //Initializing the MPU in order to enable the I2C bypass
    mpu.initialize();
    mpu.setI2CBypassEnabled(true);   
    
    Serial.println("Bypass set");

    Serial.print("Initialize compass");
    comp.initialize();
    Serial.println("compass initialized");

    // Check connection with compass
    Serial.print("Check AK8975 device connection...");
    Serial.println(mag.testConnection() ? "successful" : "failed");
}

void loop() {
    //Read the raw values from the compass in vector format
    comp.getHeading(&mx, &my, &mz);

    if (mx < min_x)
    {
        min_x = mx;
        Serial.print("Min_x: ");
        Serial.println(min_x);
    }

    if (my < min_y)
    {
        min_y = my;
        Serial.print("Min_y: ");
        Serial.println(min_y);
    }

    if (mz < min_z)
    {
        min_z = mz;
        Serial.print("Min_z: ");
        Serial.println(min_z);
    }

    if (mx > max_x)
    {
        max_x = mx;
        Serial.print("Max_x: ");
        Serial.println(max_x);
    }

    if (my > max_y)
    {
        max_y = my;
        Serial.print("Max_y: ");
        Serial.println(max_y);
    }

    if (mz > max_z)
    {
        max_z = mz;
        Serial.print("Max_z: ");
        Serial.println(max_z);
    }

    if (Serial.available())
    {
        // Gives user ability to print new caliration values
        if (Serial.read() == 'p')
        {
            Serial.println("--------------------");
            Serial.println("Calibration values:");
            Serial.print("Min X: ");
            Serial.println(min_x);
            Serial.print("Max X: ");
            Serial.println(max_x);
            Serial.print("Min Y: ");
            Serial.println(min_y);
            Serial.print("Max Y: ");
            Serial.println(max_y);
            Serial.print("Min Z: ");
            Serial.println(min_z);
            Serial.print("Max Z: ");
            Serial.println(max_z);
        }
    }
}
