#include <Adafruit_MCP4725.h>
#include <FlexCAN_T4.h>
#include <Wire.h>
#include <string>
#include <Arduino.h>

using namespace std;

// The DAC for voltage output
Adafruit_MCP4725 dac;

// The pin for the reverse switch
const int reversePin = 2;

// The boolean
bool isMoving = false;

// Timeouts
unsigned long timeout = 500;  // 50 ms timeout
bool message_received = false;

// The CAN interface
FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_16> can;
CAN_message_t msg;

void setMotorSpeed(const CAN_message_t& msg)  {
    // Print out the recieved message
    Serial.println("Received: ");
    for (int i = 0; i < msg.len; i++) {
        Serial.print(msg.buf[i], HEX);
        Serial.print(" ");
    }
    Serial.println();
    
    // Get the first byte of the message data
    uint8_t command = msg.buf[0];
    message_received = true;

    // If the command is 0xC0, set the motor speed to 0
    if (command == 0xC0) {
        dac.setVoltage(0, true);
        isMoving = false;
        return;
    } else if (command == 0xC4) {
        // If the command is 0x01, set the motor speed to 5V
        dac.setVoltage(4000, false);
        isMoving = true;
        return;
    } else if (command == 0xC6) {
        // If the command is 0xC6, reverse the motor
        digitalWrite(reversePin, LOW);
        return;
    } else if (command == 0xC8) {
        // If the command is 0xC8, stop reversing the motor
        digitalWrite(reversePin, HIGH);
        return;
    }

}

void setup(void) {
    // Start the serial terminal
    Serial.begin(115200);
    Serial.println("Welcome to Motor Control!");

    // Set the reverse pin to output
    pinMode(reversePin, OUTPUT);
    digitalWrite(reversePin, HIGH);

    // Delay by 5 seconds for startup
    delay(5000);

    // Start the CAN interface
    can.begin();
    can.setBaudRate(250000);  // 500 kbps

    // can.enableFIFO();
    // Enables interrupts on the FIFO buffer
    // can.enableFIFOInterrupt();

    // Set all mailboxes to reject all messages
    can.setMBFilter(REJECT_ALL);

    // Enable all mailboxes to be interrupt enabled
    can.enableMBInterrupts();

    // Set mailbox zero to recieve only messages with ID 0x123
    can.setMBFilter(MB0, 0x4FF);
    // Can0.setMBUserFilter(MB0, 0x123, 0x7FF); // Last parameter is the mask. This is ANDed with the ID to determine if the message is accepted

    // Set the function to run when a message is recieved
    can.onReceive(MB0, setMotorSpeed);

    // Start the DAC
    // For Adafruit MCP4725A1 the address is 0x62 (default) or 0x63 (ADDR pin tied to VCC)
    if (dac.begin(0x62, &Wire)) {
        Serial.println("DAC Ready!");
        dac.setVoltage(0, true);
    } else {
        Serial.println("DAC unknown error");
        exit(1);

        // Blink the LED
        while (1) {
            digitalWrite(LED_BUILTIN, HIGH);
            delay(500);
            digitalWrite(LED_BUILTIN, LOW);
            delay(500);
        }

    };

    Serial.println("Setup Complete");
}

// Assuming 5V input
void loop(void) {
    // unsigned long start_time = millis();
    // message_received = false;
    // while (millis() - start_time < timeout) {
    //     // Check for events
    //     can.events();

    //     // Check if message received
    //     if (message_received) {
    //         message_received = false;
    //         start_time = millis();
    //         continue;
    //     }
    // }

    // // Timeout reached
    // Serial.println("Timeout reached");

    // if (!message_received && isMoving) {
    //     // Emergency stop
    //     dac.setVoltage(0, true);

    //     // Blink the LED
    //     while (1) {
    //         digitalWrite(LED_BUILTIN, HIGH);
    //         delay(500);
    //         digitalWrite(LED_BUILTIN, LOW);
    //         delay(500);
    //     }
    // }

    can.events();
    delay(100);
}