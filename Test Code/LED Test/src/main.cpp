#include <FastLED.h>
#include <FlexCAN_T4.h>
#include <Wire.h>
#include <string>

#define NUM_LEDS 150     /* The amount of pixels/leds you have */
#define DATA_PIN_1 3     /* The pin your data line is connected to */
#define DATA_PIN_2 25    /* The pin your data line is connected to */
#define LED_TYPE WS2812B /* I assume you have WS2812B leds, if not just change it to whatever you have */

using namespace std;

int offset = 0;
bool message_received = false;
CRGB leds[NUM_LEDS];
int state = 0;  // normal state plays albertaloop colors, state 1 is emergency stopped

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

    if (command == 0xB1) {
        // If the command is 0xB1, pod is emergency stopped
        state = 1;
        return;
    } else if (command == 0xB0) {
        // If the command is 0xB0, pod is operating normally
        state = 0;
    }
}

void setup(void) {
    // Start the serial terminal
    Serial.begin(115200);
    Serial.println("Welcome to LED Controller!");

    // Set the LED pin to output
    FastLED.addLeds<LED_TYPE, DATA_PIN_1>(leds, NUM_LEDS);
    FastLED.addLeds<LED_TYPE, DATA_PIN_2>(leds, NUM_LEDS);

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
    can.setMBFilter(MB0, 0x5FF);
    // Can0.setMBUserFilter(MB0, 0x123, 0x7FF); // Last parameter is the mask. This is ANDed with the ID to determine if the message is accepted

    // Set the function to run when a message is recieved
    can.onReceive(MB0, SetRelayState);

    Serial.println("Setup Complete");
}

// Assuming 5V input
void loop(void) {
    // Check for events
    can.events();
    // Serial.println("Checking for messages");

    if (state == 0) {
        // Set the LED to AlbertaLoop Colors
        for (int i = 0; i < NUM_LEDS; i++) {
            leds[i] = CRGB(0, 0, 255);  // Set RGB values to create blue
        }
        for (int i = 0; i < 75; i++) {
            leds[(i + offset) % 150] = CRGB(155, 255, 0);  // Set RGB values to create blue
        }

        offset++;
        if (offset >= NUM_LEDS) {
            offset = 0;
        }

        FastLED.show();

    } else if (state == 1) {
        // Emergency stop
        for (int i = 0; i < NUM_LEDS; i++) {
            leds[i] = CRGB(0, 255, 0);  // Set RGB values to red
        }
        FastLED.show();
        
    }

    delay(100);
}