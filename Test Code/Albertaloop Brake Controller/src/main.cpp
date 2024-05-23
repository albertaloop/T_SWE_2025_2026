
#include <FlexCAN_T4.h>
#include <Wire.h>
#include <string>

using namespace std;

// Pin Definitions
const int contactorPin = 24;
const int brakesPin = 25;

// The boolean
bool isReleased = false;

// Timeouts
unsigned long timeout = 50;  // 50 ms timeout
bool message_received = false;

// The CAN interface
FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_16> can;
CAN_message_t msg;

void SetRelayState(const CAN_message_t& msg) {
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

    // If the command is 0xA0, turn off contactor and engage brakes
    if (command == 0xA0) {
        digitalWrite(contactorPin, HIGH);
        digitalWrite(brakesPin, HIGH);
        isReleased = false;
        return;
    } else if (command == 0xA2) {
        // If the command is 0xA2, turn on the contactor
        digitalWrite(contactorPin, LOW);
        return;
    } else if (command == 0xA4) {
        // If the command is 0xC6, disengage brakes
        digitalWrite(brakesPin, LOW);
        isReleased = true;
        return;
    } else if (command == 0xA6) {
        // If the command is 0xA6  engage brakes
        digitalWrite(brakesPin, HIGH);
        isReleased = false;
        return;
    }

}

void setup(void) {
    // Start the serial terminal
    Serial.begin(115200);
    Serial.println("Welcome to Brake Control!");

    // Set the reverse pin to output
    pinMode(brakesPin, OUTPUT);
    pinMode(contactorPin, OUTPUT);
    digitalWrite(brakesPin, HIGH);
    digitalWrite(contactorPin, HIGH);

    // Delay by 5 seconds for startup
    delay(5000);

    // Start the CAN interface
    can.begin();
    can.setBaudRate(250000);  // 500 kbps

    // Set all mailboxes to reject all messages
    can.setMBFilter(REJECT_ALL);

    // Enable all mailboxes to be interrupt enabled
    can.enableMBInterrupts();

    // Set mailbox zero to recieve only messages with ID 0x123
    can.setMBFilter(MB0, 0x3FF);
    // Can0.setMBUserFilter(MB0, 0x123, 0x7FF); // Last parameter is the mask. This is ANDed with the ID to determine if the message is accepted

    // Set the function to run when a message is recieved
    can.onReceive(MB0, SetRelayState);

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

    // Timeout reached
    // Serial.println("Timeout reached");
    can.events();
    delay(100);

    // if (!message_received && isReleased) {
    //     // Emergency stop
    //     digitalWrite(contactorPin, HIGH);
    //     digitalWrite(brakesPin, HIGH);

    //     // Blink the LED
    //     while (1) {
    //         digitalWrite(LED_BUILTIN, HIGH);
    //         delay(500);
    //         digitalWrite(LED_BUILTIN, LOW);
    //         delay(500);
    //     }
    // }
}