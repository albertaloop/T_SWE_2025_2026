#pragma once

#define FORWARD             0xc4
#define STOP                0xc0
#define REVERSE_ON          0xc6
#define REVERSE_OFF         0xc8

#define BRAKE_ESTOP         0xa0
#define BRAKE_PREP_LAUNCH   0xa2
#define BRAKE_LAUNCH        0xa4
#define BRAKE_CRAWL         0xa6

#define LED_FAULT           0xb1
#define LED_NORMAL          0xb0

#define INVALID             0xff
#define WATCHDOG            0x99

#define NUM_POSSIBLE_CMDS   256

extern bool validCmds[NUM_POSSIBLE_CMDS];

void initValidCmds();