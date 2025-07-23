from config import *
from utils.formatPayload import PodMessage
import can

def sendCanMessage(podMessage):
    with can.Bus(interface='socketcan', channel='can0', bitrate=250000) as bus:
        for id in STATE_FRAMES[podMessage.gui_command]:
            print(id)
            msg = can.Message(
                arbitration_id=id, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False
            )
            try:
                bus.send(msg)
                print(f"Message sent on {bus.channel_info}")
            except can.CanError:
                print("Message NOT sent")


