#include "CircularBuffer.h"

CircularBuffer::CircularBuffer(int num_bits)
{
  this->size = (1 << num_bits);
  for (int i = 0; i < size; ++i)
  {
    buffer.push_back(0);
  }
}

bool CircularBuffer::push(int val)
{
  if ((write_ptr+1 % size) != read_ptr)
  {
    buffer[write_ptr] = val;
    write_ptr++;
    write_ptr &= size-1;
    return true;
  }
  return false;
}

bool CircularBuffer::pop(int * val)
{
  if (write_ptr != read_ptr)
  {
    *val = buffer[read_ptr];
    read_ptr++;
    read_ptr &= size-1;
    return true;
  }
  return false;
}