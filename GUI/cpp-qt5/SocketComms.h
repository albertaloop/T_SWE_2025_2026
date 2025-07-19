#include "CircularBuffer.h"
#include <cstdint>



class SocketComms
{
private:
  void setupSockets();
  void threadFunc();
  bool getNextCmd(uint8_t * cmd);
  CircularBuffer * sendBuffer;
  CircularBuffer * responseBuffer;


public:
  SocketComms(CircularBuffer * sendBuffer, CircularBuffer * responseBuffer);
  void start();
};


