/**************************************************************************/
/*! 
    @file     trianglewave.pde
    @author   Adafruit Industries
    @license  BSD (see license.txt)

    This example will generate a triangle wave with the MCP4725 DAC.   

    This is an example sketch for the Adafruit MCP4725 breakout board
    ----> http://www.adafruit.com/products/935
 
    Adafruit invests time and resources providing this open source code, 
    please support Adafruit and open-source hardware by purchasing 
    products from Adafruit!
*/
/**************************************************************************/
#include <Wire.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac;

void setup(void) {
  Serial.begin(115200);
  Serial.println("Hello!");

  delay(10000);

  

  // For Adafruit MCP4725A1 the address is 0x62 (default) or 0x63 (ADDR pin tied to VCC)
  // For MCP4725A0 the address is 0x60 or 0x61
  // For MCP4725A2 the address is 0x64 or 0x65
  if (dac.begin(0x62, &Wire)){
    Serial.println("DAC Ready!");
  } else {
    Serial.println("DAC unknown error");
  
  };
    
  Serial.println("Generating a triangle wave");
}

// Assuming 5V input
void loop(void) {
    uint32_t counter;
    // Set the volatage on the DAC to 0V
    dac.setVoltage(0, false);
    Serial.println("0V");
    // Delay by 5 seconds
    delay(5000);

    // Set the voltage to 1V
    dac.setVoltage(1024, false);
    Serial.println("1V");

    // Delay by 5 seconds
    delay(5000);

    // Set the voltage to 2V
    dac.setVoltage(2048, false);
    Serial.println("2V");

    // Delay by 5 seconds
    delay(5000);

    // Set the voltage to 3V
    dac.setVoltage(3072, false);
    Serial.println("3V");

    // Delay by 5 seconds
    delay(5000);

    // Set the voltage to 4V
    dac.setVoltage(4000, false);
    Serial.println("4V");

    // Delay by 5 seconds
    delay(5000);




}