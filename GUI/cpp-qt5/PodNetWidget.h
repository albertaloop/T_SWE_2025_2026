#pragma once

#include <QWidget>

typedef struct
{
  QPoint pos;
  int state;
  QString status;
  QString name;
} CanNode_t;

#define NUM_CAN_NODES       4

#define STATE_MACHINE_NODE  0
#define BRAKE_NODE          1
#define MOTOR_NODE          2
#define LED_NODE            3

#define CAN_NODE_DISCONNECTED 0
#define CAN_NODE_CONNECTED    1



class PodNetWidget : public QWidget
{
private:
  /* data */
  int leftBorder;
  int rightBorder;
  int topBorder;
  int bottomBorder;

  int ledX;
  int ledY;
  int stateMachineX;
  int stateMachineY;
  int brakeX;
  int brakeY;
  int motorX;
  int motorY;

  int nodeGap = 40;

  int nodeHeight = 200;
  int nodeWidth = 160;

public:
  PodNetWidget(QWidget *parent = nullptr);

  CanNode_t nodeInfo[NUM_CAN_NODES];


protected:
  void paintEvent(QPaintEvent * event) override;
  QSize sizeHint() const override;
  QSize minimumSizeHint() const override;

};

