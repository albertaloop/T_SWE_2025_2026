#include "PodNetWidget.h"
#include <QPainter>
#include <QLinearGradient>






PodNetWidget::PodNetWidget(QWidget *parent) : QWidget(parent)
{


  for (int i = 0; i < NUM_CAN_NODES; ++i)
  {
    nodeInfo[i].state = CAN_NODE_DISCONNECTED;
    nodeInfo[i].status = "Disconnected";
  }
  nodeInfo[STATE_MACHINE_NODE].pos = QPoint(400, 240);
  nodeInfo[BRAKE_NODE].pos = QPoint(0, 0);
  nodeInfo[MOTOR_NODE].pos = QPoint(240, 0);
  nodeInfo[LED_NODE].pos = QPoint(0, 240);

  nodeInfo[STATE_MACHINE_NODE].name = "State Machine";
  nodeInfo[BRAKE_NODE].name = "Brakes";
  nodeInfo[MOTOR_NODE].name = "Motor";
  nodeInfo[LED_NODE].name = "LEDs";


}

void PodNetWidget::paintEvent(QPaintEvent * event)
{
  QPainter painter(this);
  // Draw a line from (10, 50) to (150, 50)
  
  painter.drawLine(100, 200, 500, 200);


  for (int i = 0; i < NUM_CAN_NODES; ++i) {
      // Set the brush based on the state
      QLinearGradient gradient(nodeInfo[i].pos.x(),
                               nodeInfo[i].pos.y(),
                               nodeInfo[i].pos.x() + 200,
                               nodeInfo[i].pos.y() + 160);
      if (nodeInfo[i].state == CAN_NODE_CONNECTED)
      {
        // Green gradient
        gradient.setColorAt(0, Qt::green);
        gradient.setColorAt(1, QColor(200, 255, 200)); // Light green to the right
      }
      else
      {
        // Red gradient
        gradient.setColorAt(0, Qt::red);
        gradient.setColorAt(1, QColor(255, 200, 200)); // Light red to the right
      }
      painter.setBrush(QBrush(gradient));
      QRect rect(nodeInfo[i].pos.x(),
                 nodeInfo[i].pos.y(),
                 200,
                 160);
      painter.drawRect(rect);

      painter.setPen(Qt::black);

      painter.drawText(rect.topLeft() + QPoint(5, 15), nodeInfo[i].name);  // Offset by 5 pixels right and 15 pixels down

      QFontMetrics fm(painter.font());
      int textWidth = fm.horizontalAdvance(nodeInfo[i].status);
      int textHeight = fm.height();
      int x = rect.x() + (rect.width() - textWidth) / 2;
      int y = rect.y() + (rect.height() + textHeight) / 2 - fm.descent();
      painter.drawText(x, y, nodeInfo[i].status);
  }

  painter.drawLine(100, 160, 100, 200);
  painter.drawLine(340, 160, 340, 200);
  painter.drawLine(100, 200, 100, 240);
  painter.drawLine(500, 200, 500, 240);


}

QSize PodNetWidget::sizeHint() const
{
  return QSize(800,500);
}

QSize PodNetWidget::minimumSizeHint() const
{
  return QSize(800,500);
}
