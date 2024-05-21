#include <Adafruit_MCP4725.h>
#include <FlexCAN_T4.h>
#include <Wire.h>

// The DAC for voltage output
Adafruit_MCP4725 dac;

// The CAN interface
FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> can;

void SetMotorSpeed(int speed, bool direction){

}


void setup(void) {
    // Start the serial terminal
    Serial.begin(115200);
    Serial.println("Welcome to Motor Control!");

    // Delay by 5 seconds for startup
    delay(5000);

    // Start the CAN interface
    can.begin();
    can.setBaudRate(500000);  // 500 kbps

    // Set all mailboxes to reject all messages
    can.setMBFilter(REJECT_ALL);

    // Enable all mailboxes to be interrupt enabled
    can.enableMBInterrupts();

    // Set mailbox zero to recieve only messages with ID 0x123
    can.setMBFilter(MB0, 0x123);
    // Can0.setMBUserFilter(MB0, 0x123, 0x7FF); // Last parameter is the mask. This is ANDed with the ID to determine if the message is accepted

    // Set the function to run when a message is recieved
    can.onReceive(MB0, canSniff);

    Serial.begin(115200);
    Serial.println("Hello!");

    delay(10000);

    // For Adafruit MCP4725A1 the address is 0x62 (default) or 0x63 (ADDR pin tied to VCC)
    // For MCP4725A0 the address is 0x60 or 0x61
    // For MCP4725A2 the address is 0x64 or 0x65
    if (dac.begin(0x62, &Wire)) {
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