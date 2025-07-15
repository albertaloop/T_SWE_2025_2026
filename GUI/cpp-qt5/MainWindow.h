#pragma once

#include <QMainWindow>
#include <QWidget>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPushButton>
#include <QTimer>

#include <map>
#include <functional>
#include <cstdint>

#include "Commands.h"

#include "PodNetWidget.h"
#include "CircularBuffer.h"

class MainWindow : public QMainWindow
{
private:
  QVBoxLayout * topVLayout;
  QHBoxLayout * podNetHLayout;
  QHBoxLayout * btnHLayout;
  QHBoxLayout * motorBtnHLayout;
  QHBoxLayout * brakeBtnHLayout;
  QVBoxLayout * brakeMotorBtnVLayout;

  QVBoxLayout * ledBtnVLayout;

  QPushButton * motorForwardBtn;
  QPushButton * motorStopBtn;
  QPushButton * normalStopBtn;

  // QPushButton * motorReverseOnBtn;
  // QPushButton * motorReverseOffBtn;
  
  QPushButton * brakeEstopBtn;
  QPushButton * brakePrepareBtn;
  QPushButton * brakeReleaseBtn;
  QPushButton * brakeEngageBtn;

  QPushButton * ledNormalBtn;
  QPushButton * ledFaultBtn;

  PodNetWidget * podNetWidget;
  CircularBuffer * sendBuffer;
  CircularBuffer * responseBuffer;

  QTimer * responseTimer;

  bool getNextResponse(uint8_t * rsp);

  std::map<uint8_t, std::function<void(uint8_t)>> tcp_responses;

  void rspDefaultCallback(uint8_t rsp);

  // Motor response callbacks
  void rspForwardCallback(uint8_t rsp);
  void rspStopCallback(uint8_t rsp);
  void rspReverseOffCallback(uint8_t rsp);
  void rspReverseOnCallback(uint8_t rsp);

  // Brake Response callbacks
  void rspBrakeLaunchCallback(uint8_t rsp);
  void rspBrakeStopCallback(uint8_t rsp);
  void rspBrakeCrawlCallback(uint8_t rsp);
  void rspBrakePrepLaunchCallback(uint8_t rsp);

  // LED response callbacks
  void rspLEDFaultCallback(uint8_t rsp);
  void rspLEDNormalCallback(uint8_t rsp);


public:
  MainWindow(CircularBuffer * sendBuffer,
             CircularBuffer * responseBuffer,
             QWidget *parent = nullptr);

private slots:
    void checkResponses();

protected:
  QSize sizeHint() const override;
  QSize minimumSizeHint() const override;
};

