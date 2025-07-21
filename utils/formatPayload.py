from dataclasses import dataclass
import struct
from config import *

# Data to be sent over lora
@dataclass
class PodMessage:
    fsm_state: bytes = bytes(1)
    can_brake: bytes = bytes(4)
    can_motors: bytes = bytes(4)
    can_led: bytes = bytes(4)
    gui_command: str = ""

# Formats 2 byte payload to a list
def splitPayload(payload):
  return [(payload >> 8) & 0xFF, payload & 0xFF]

def reconstructPayload(payload):
  return (payload[0] << 8) | payload[1]

# Converts string to list of 2 byte items suitable for lora
def convertStringToByteList(string):
  return [ord(c) for c in string]

def convertByteListToString(list):
  return bytes(list).decode("utf-8",'ignore')

# 1 byte for the state, 4 bytes for each can message
fmt = '1s4s4s4s'

def packPayload(payload):
  return struct.pack(
    fmt,
    payload.fsm_state,
    payload.can_brake,
    payload.can_motors,
    payload.can_led
  ) + payload.gui_command.encode('ascii')


def unpackPayload(payload):
  payload = bytes(payload)
  fsm_state = payload[0:1]
  can_brake = payload[1:5]
  can_motors = payload[5:9]
  can_led = payload[9:13]
  gui_command = payload[13:].decode('ascii')

  msg_received = PodMessage(
      fsm_state = fsm_state,
      can_brake = can_brake,
      can_motors = can_motors,
      can_led = can_led,
      gui_command = "test"
  )
  
  return msg_received

# payload = PodMessage(
#     fsm_state=1,
#     can_brake = bytes([0x11, 0x02, 0x03] + [0x00]*7),  # pad to 10 bytes
#     can_motors = bytes([0x10, 0x20, 0x30] + [0x00]*7),
#     can_led = bytes([0xFF]*10),
#     gui_command="ready"
# )

# print(unpackPayload(list(packPayload(payload))))
