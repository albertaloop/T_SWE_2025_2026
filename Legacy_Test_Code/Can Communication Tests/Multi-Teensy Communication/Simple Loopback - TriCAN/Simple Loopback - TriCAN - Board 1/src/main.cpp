/*
  This program will set up a CAN interface to recieve messages.
  The same message is then sent back to the sender.
  It will light up the LED when a message is recieved.
  This program will inject the initial message to the bus.
*/

#include <Arduino.h>
#include <FlexCAN_T4.h>

// Instantiate the CAN interface at CAN1
FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> Can0;
// Instantiate the second interface at CAN2
FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_16> Can1;
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
  msg2.id = 0x0;
  msg2.buf[0] = 3;
  Can0.write(msg2);
}


void setup() {
  //Set the LED pin as output
  pinMode(LED_BUILTIN, OUTPUT);
  // Turn on the LED
  digitalWrite(LED_BUILTIN, HIGH);
  
  // Start serial
  Serial.begin(115200);

  // Instantiate CAN communication with a FIFO buffer
  Can0.begin();
  Can0.setBaudRate(500000); // 500 kbps

  // Set all mailboxes to reject all messages
  Can0.setMBFilter(REJECT_ALL);

  // Enable all mailboxes to be interrupt enabled
  Can0.enableMBInterrupts();

  // Set mailbox zero to recieve only messages with ID 0x123
  Can0.setMBFilter(MB0, 0x123);
  // Can0.setMBUserFilter(MB0, 0x123, 0x7FF); // Last parameter is the mask. This is ANDed with the ID to determine if the message is accepted

  // Set the function to run when a message is recieved
  Can0.onReceive(MB0, canSniff);

  // Instantiate CAN communication with a FIFO buffer
  Can1.begin();
  Can1.setBaudRate(500000); // 500 kbps
  // Set all mailboxes to reject all messages
  Can1.setMBFilter(REJECT_ALL); // Transmit only

  // Write the initial message to the bus
  msg.id = 0x0;
  msg.buf[0] = 3;
  Can1.write(msg);

  Can0.mailboxStatus();

}

void loop() {
  // Checks for any CAN events
  Can0.events();

  Serial.println("Testing");
  delay(100);
}



