
// https://chat.openai.com/share/3e517cd8-5c45-46d2-beae-4fc47398b9a4

#include <Arduino.h>
#include <FlexCAN_T4.h>

// Instantiate CAN interfaces
FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> Can0;   // Recieve
FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_16> can2;   // Transmit
CAN_message_t msg;

// Function called when a message is recieved
// Similar to a thread function
void canSniff(const CAN_message_t &msg) {
  Serial.print("MB "); Serial.print(msg.mb);
  Serial.print("  OVERRUN: "); Serial.print(msg.flags.overrun);
  Serial.print("  LEN: "); Serial.print(msg.len);
  Serial.print(" EXT: "); Serial.print(msg.flags.extended);
  Serial.print(" TS: "); Serial.print(msg.timestamp);
  Serial.print(" ID: "); Serial.print(msg.id, HEX);
  Serial.print(" Buffer: ");
  for ( uint8_t i = 0; i < msg.len; i++ ) {
    Serial.print(msg.buf[i], HEX); Serial.print(" ");
  } Serial.println();
}

void setup() {
  // Start serial
  Serial.begin(115200); delay(400);

  // Start CAN communication
  Can0.begin();
  Can0.setBaudRate(500000);

  Can0.

  // Enables the use of a FIFO buffer
  Can0.enableFIFO();
  // Enables interrupts on the FIFO buffer
  Can0.enableFIFOInterrupt();
  // Sets the canSniff function to run when a message is recieved
  Can0.onReceive(canSniff);
  
  // Init the transmit interface
  can2.begin();
  can2.setBaudRate(500000);

  delay(5000);
  
  // Prints out some information on the mailboxes
  Can0.mailboxStatus();
}

void loop() {
  // Checks for any CAN events
  Can0.events();


  // Randomizes the ID and data of the message
  CAN_message_t msg;
  msg.id = random(0x1,0x7FE);
  for ( uint8_t i = 0; i < 8; i++ ) msg.buf[i] = i + 1;
  can2.write(msg);

  delay(1000);
}

