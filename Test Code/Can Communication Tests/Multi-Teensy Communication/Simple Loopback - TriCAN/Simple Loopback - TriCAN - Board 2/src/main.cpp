/*
  This program will set up a CAN interface to recieve messages.
  The same message is then sent back to the sender.
  It will light up the LED when a message is recieved.
*/

#include <Arduino.h>
#include <FlexCAN_T4.h>

// Instantiate the CAN interface at CAN1
FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> Can0;
CAN_message_t msg;

// Function called when a message is recieved
// Similar to a thread function
void canSniff(const CAN_message_t &msg) {
  // Turn on the LED
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);

  // Send a message back
  CAN_message_t msg2;
  msg2.id = 0x123;
  msg2.buf[0] = 5;
  Can0.write(msg2);
}


void setup() {
  //Set the LED pin as output
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Start serial
  Serial.begin(115200);

  // Instantiate CAN communication with a FIFO buffer
  Can0.begin();
  Can0.setBaudRate(500000); // 500 kbps
  // Enables the use of a FIFO buffer
  Can0.enableFIFO();
  // Enables interrupts on the FIFO buffer
  Can0.enableFIFOInterrupt();
  Can0.onReceive(canSniff); // Set the function to run when a message is recieved

}

void loop() {
  // Checks for any CAN events
  Can0.events();

  Serial.println("Testing");
  delay(100);
}
