#include <QApplication>

#include "MainWindow.h"
#include "SocketComms.h"
#include "CircularBuffer.h"
#include "Commands.h"

int main(int argc, char *argv[])
{

  QApplication app(argc, argv);

  initValidCmds();

  CircularBuffer * sendBuffer = new CircularBuffer(3);
  CircularBuffer * responseBuffer = new CircularBuffer(3);

  SocketComms socketComms(sendBuffer, responseBuffer);
  MainWindow window(sendBuffer, responseBuffer);
  socketComms.start();
  window.show();
  return app.exec();
}