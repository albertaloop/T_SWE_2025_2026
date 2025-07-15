#include "Commands.h"

bool validCmds[NUM_POSSIBLE_CMDS];


void initValidCmds()
{
  for (int i = 0; i < NUM_POSSIBLE_CMDS; ++i)
  {
    validCmds[i] = false;
  }
  validCmds[FORWARD] = true;
  validCmds[STOP] = true;
  validCmds[REVERSE_ON] = true;
  validCmds[REVERSE_OFF] = true;
  validCmds[BRAKE_ESTOP] = true;
  validCmds[BRAKE_PREP_LAUNCH] = true;
  validCmds[BRAKE_LAUNCH] = true;
  validCmds[BRAKE_CRAWL] = true;
  validCmds[LED_FAULT] = true;
  validCmds[LED_NORMAL] = true;
}