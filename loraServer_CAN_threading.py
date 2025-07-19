#!/usr/bin/env python3
import threading
import time
import sys

#import rospy
#import can

# CAN/FSM config constants
from config import (
    CAN_INTERFACE,
    BRAKE_ID_START, BRAKE_ID_END,
    MOTOR_ID_START, MOTOR_ID_END,
    LED_ID_START, LED_ID_END,
    BRAKE_ENGAGE_CMD, BRAKE_DISENGAGE_CMD,
    MOTOR_STOP_CMD, MOTOR_START_10_CMD, MOTOR_START_30_CMD,
    MOTOR_START_50_CMD, MOTOR_START_70_CMD, MOTOR_START_100_CMD,
    BRAKE_HEARTBEAT_ID, MOTOR_HEARTBEAT_ID, LED_HEARTBEAT_ID,
    DEFAULT_STATE, DEFAULT_TRANSITIONS, HEARTBEAT_TIMEOUT,
    STATE_FAULT, STATE_SAFE, STATE_CRAWLING, STATE_BRAKING
)

# Bring in your LoRa server implementation
sys.path.append('/home/ubuntu/pySX127x')
from lora_server import mylora, BOARD
from SX127x.LoRa import BW, CODING_RATE, MODE

# Global FSM state and heartbeat timers
CANBUS = None
state = DEFAULT_STATE.copy()
signal_time_elapsed = {'brakes': 0, 'motor': 0, 'LED': 0}

'''
def change_state(next_state):
    """Switch to next_state if valid."""
    current = next(k for k, v in state.items() if v)
    if next_state in DEFAULT_TRANSITIONS[current]:
        state[current], state[next_state] = False, True
        rospy.loginfo(f"[FSM] {current} → {next_state}")


def send_can(arbitration_id, data=None):
    """Helper to send a CAN message."""
    if data is None:
        data = [0x00, 0x00, 0x00, 0x00]
    try:
        CANBUS.send(can.Message(arbitration_id=arbitration_id, data=data))
    except can.CanError as e:
        rospy.logwarn(f"[CAN] send failed: {e}")


def read_can_message(msg):
    """Decode a received CAN message and update FSM or timers."""
    arb = msg.arbitration_id & 0xFFF
    cmd = arb & 0x0FF

    # --- Brake controller messages ---
    if BRAKE_ID_START <= arb <= BRAKE_ID_END:
        if cmd == (BRAKE_ENGAGE_CMD & 0x0FF):
            change_state(STATE_BRAKING)
        elif cmd == (BRAKE_DISENGAGE_CMD & 0x0FF):
            change_state(STATE_SAFE)
        elif arb == BRAKE_HEARTBEAT_ID:
            signal_time_elapsed['brakes'] = 0

    # --- Motor controller messages ---
    elif MOTOR_ID_START <= arb <= MOTOR_ID_END:
        if cmd == (MOTOR_STOP_CMD & 0x0FF):
            change_state(STATE_SAFE)
        elif cmd in {
            MOTOR_START_10_CMD & 0x0FF,
            MOTOR_START_30_CMD & 0x0FF,
            MOTOR_START_50_CMD & 0x0FF,
            MOTOR_START_70_CMD & 0x0FF,
            MOTOR_START_100_CMD & 0x0FF
        }:
            change_state(STATE_CRAWLING)
        elif arb == MOTOR_HEARTBEAT_ID:
            signal_time_elapsed['motor'] = 0

    # --- LED controller messages ---
    elif LED_ID_START <= arb <= LED_ID_END:
        if arb == LED_HEARTBEAT_ID:
            signal_time_elapsed['LED'] = 0
        else:
            idx = list(state.values()).index(True)
            led_msg_id = LED_ID_START + idx
            send_can(arbitration_id=led_msg_id)
            return

    # Acknowledge any other CAN IDs
    send_can(arbitration_id=arb)


def can_thread():
    """Thread loop: receive CAN messages and monitor heartbeats."""
    global CANBUS
    rospy.loginfo("[CAN] Thread started")
    CANBUS = can.interface.Bus(bustype='socketcan', channel=CAN_INTERFACE)

    while not rospy.is_shutdown():
        msg = CANBUS.recv(timeout=1.0)
        if msg:
            read_can_message(msg)

        # Heartbeat watchdog
        for key in signal_time_elapsed:
            signal_time_elapsed[key] += 1
            if signal_time_elapsed[key] > HEARTBEAT_TIMEOUT:
                rospy.logerr(f"[CAN] {key} heartbeat lost → fault")
                change_state(STATE_FAULT)
                signal_time_elapsed[key] = 0

        time.sleep(0.01)

'''
def lora_thread():
    """Thread entry point: spin up your existing mylora server."""
    BOARD.setup()
    BOARD.reset()

    lora = mylora(verbose=False)
    # mirror your lora_server.py configuration:
    lora.set_pa_config(pa_select=1, max_power=21, output_power=15)
    lora.set_bw(BW.BW125)
    lora.set_coding_rate(CODING_RATE.CR4_8)
    lora.set_spreading_factor(12)
    lora.set_rx_crc(True)
    lora.set_low_data_rate_optim(True)
    lora.set_freq(915)

    # Blocking start() method loops send/receive/ACK
    try:
        lora.start()
    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()


if __name__ == '__main__':
    #rospy.init_node('pod_comm_node', anonymous=False)
    print('pod_comm_node')
    #threading.Thread(target=can_thread, name="CAN-Thread", daemon=True).start()
    threading.Thread(target=lora_thread, name="LoRa-Thread", daemon=True).run()

    #rospy.spin()