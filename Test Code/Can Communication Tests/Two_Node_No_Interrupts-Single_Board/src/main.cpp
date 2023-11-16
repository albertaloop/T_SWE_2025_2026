/*
  Super simple two node CAN communication network
  Every time checks if there is availible data
  The same message is passed back and forth between the nodes and is printed every time
*/

#include <Arduino.h>
#include <FlexCAN_T4.h>

// Declare the two instances of CANBUS
FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> can1;
FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_16> can2;
CAN_message_t msg;

void setup() {
  // Start CAN1 and set baud rate
  // Transmit
  can1.begin();
  can1.setBaudRate(250000);

  // Start CAN2 and set baudrate
  // Recieve
  can2.begin();
  can2.setBaudRate(250000);

  // Start serial
  Serial.begin(115200);

  // Write initial message
  msg.buf[0] = 5;
  can2.write(msg);
  Serial.println("Write Inital Message!");

  delay(5000);
}

void loop() {
  // Read/write
  if ( can1.read(msg) ) {
    Serial.print("CAN1 "); 
    Serial.print("MB: "); Serial.print(msg.mb);
    Serial.print("  ID: 0x"); Serial.print(msg.id, HEX );
    Serial.print("  EXT: "); Serial.print(msg.flags.extended );
    Serial.print("  LEN: "); Serial.print(msg.len);
    Serial.print(" DATA: ");
    for ( uint8_t i = 0; i < 8; i++ ) {
      Serial.print(msg.buf[i]); Serial.print(" ");
    }
    Serial.print("  TS: "); Serial.println(msg.timestamp);

    can1.write(msg);
  }
  
  delay(1000);

  if ( can2.read(msg) ) {
    Serial.print("CAN3 "); 
    Serial.print("MB: "); Serial.print(msg.mb);
    Serial.print("  ID: 0x"); Serial.print(msg.id, HEX );
    Serial.print("  EXT: "); Serial.print(msg.flags.extended );
    Serial.print("  LEN: "); Serial.print(msg.len);
    Serial.print(" DATA: ");
    for ( uint8_t i = 0; i < 8; i++ ) {
      Serial.print(msg.buf[i]); Serial.print(" ");
    }
    Serial.print("  TS: "); Serial.println(msg.timestamp);

    can2.write(msg);
  }

  delay(1000);
}

