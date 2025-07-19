#include "SocketComms.h"
#include "Commands.h"

#include <sys/socket.h>
#include <netdb.h>
#include <sys/types.h>
#include <unistd.h>
#include <functional>
#include <cstring>
#include <thread>
#include <fcntl.h>

#include <iostream>
#include <cstdio>  // for perror

static int reverse_state = REVERSE_OFF;
static int sock_fd;

struct addrinfo *pod_address;
struct addrinfo hints;

static void set_nonblocking(int fd)
{
  int flags = fcntl(fd, F_GETFL, 0);
  if (flags < 0)
  {
      perror("Could not get socket flags with F_GETFD");
      exit(1);
  }

  flags |= O_NONBLOCK;
  int rv = fcntl(fd, F_SETFL, flags);
  if (rv < 0)
  {
      perror("Could not set socket flags with F_SETFD");
      exit(1);
  }

  fcntl(fd, O_NONBLOCK);
}

SocketComms::SocketComms(CircularBuffer * sendBuffer, CircularBuffer * responseBuffer)
{
  this->responseBuffer = responseBuffer;
  this->sendBuffer = sendBuffer;
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

void SocketComms::start()
{
  std::thread t(std::bind(&SocketComms::threadFunc, this));
  t.detach();
}

void SocketComms::setupSockets()
{
  hints.ai_socktype = SOCK_STREAM;
  std::cout << "setting up sockets" << std::endl;
  int rv;
  rv = getaddrinfo("192.168.1.10", "5000", &hints, &pod_address);
  // rv = getaddrinfo("127.0.0.1", "5000", &hints, &pod_address);

  if (rv != 0)
  {
    perror("Could not get requested address.");
    exit(1);
  }

  std::cout << "Creating socket" << std::endl;

  sock_fd = socket(pod_address->ai_family , pod_address->ai_socktype, pod_address->ai_protocol);
  if (sock_fd < 0)
  {
    perror("Could not create socket.");
    exit(1);
  }


  freeaddrinfo(pod_address);
  std::cout << "connecting to pod" << std::endl;

  rv = connect(sock_fd, pod_address->ai_addr, pod_address->ai_addrlen);
  if (rv < 0)
  {
      std::cout << "could not connect" << std::endl;

    perror("Could not connect to pod.");
    exit(1);
  }
  set_nonblocking(sock_fd);

  std::cout << "sockets set up" << std::endl;

}

bool SocketComms::getNextCmd(uint8_t * cmd)
{
  int val;
  bool rv = sendBuffer->pop(&val);
  if (rv && validCmds[(uint8_t)val])
  {
    *cmd = (uint8_t)val;
    return true;
  }
  return false;
}

void SocketComms::threadFunc()
{
  setupSockets();
  struct timespec loop_delay;
  loop_delay.tv_sec = 0;
  loop_delay.tv_nsec = 1000000;
  //char recv_buf[2048];
  uint8_t recv_buf;
  uint8_t cmd_msg;
  int nbytes;
  int count = 0;
  while(1)
  {
    count++;
    if (count >= 40)
    {
      count = 0;
      printf("sending watchdog\n");
      int watchDog = WATCHDOG;
      nbytes = send(sock_fd, &watchDog, sizeof(watchDog), 0);
      if (nbytes < 0) {
          if (errno == EAGAIN || errno == EWOULDBLOCK) {
              //printf("Send would block, try again later\n");
          } else {
            perror("Send failed");
            close(sock_fd);
          }
      } else {
          printf("Sent %zd bytes\n", nbytes);
      }
    }
    
    if (getNextCmd(&cmd_msg))
    {
      printf("sending valid cm\n");
      nbytes = send(sock_fd, &cmd_msg, sizeof(cmd_msg), 0);
      if (nbytes < 0) {
          if (errno == EAGAIN || errno == EWOULDBLOCK) {
              //printf("Send would block, try again later\n");
          } else {
            perror("Send failed");
            close(sock_fd);
          }
      } else {
          printf("Sent %zd bytes\n", nbytes);
      }
    }

    // memset(recv_buf, 0, 2048);
    // recv_buf[2047] = '\0';
    nbytes = recv(sock_fd, &recv_buf, sizeof(cmd_msg), 0);
    if (nbytes < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            //printf("Receive would block, try again later\n");
        } else {
            perror("Recv");
        }
    } else if (nbytes == 0) {
        printf("Connection closed by the server\n");
        responseBuffer->push(recv_buf);
    } else {
        //printf("Received: %x\n", recv_buf);
    }
    nanosleep(&loop_delay, NULL);



  }
  close(sock_fd);
}


