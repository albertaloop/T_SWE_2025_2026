#pragma once

#include <vector>

class CircularBuffer
{
private:
  /* data */
  std::vector<int> buffer;
  int write_ptr = 0;
  int read_ptr = 0;
  int size;
public:
  CircularBuffer(int num_bits);
  bool push(int val);
  bool pop(int * val);
};


