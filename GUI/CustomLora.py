from time import sleep
from pySX127x.SX127x.LoRa import *
from pySX127x.SX127x.board_config import BOARD
from PyQt5.QtCore import QObject, pyqtSignal
from utils.formatPayload import reconstructPayload, splitPayload
from config import *

def get_state(msg):
    payload = reconstructPayload(msg)
    print("Got payload:", payload)
    return STATE_BRAKING

class CustomLora(LoRa, QObject):
    state_updated = pyqtSignal(str)  # the new state will be emitted here

    def __init__(self, verbose=False):
        LoRa.__init__(self, verbose)
        QObject.__init__(self) 
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def on_rx_done(self):
        BOARD.led_on()
        print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)

        # Parse state from payload then emit signal to window
        new_state = get_state(payload)
        self.state_updated.emit(new_state)
        BOARD.led_off()

    def on_tx_done(self):
        print("\nTxDone")
        print(self.get_irq_flags())

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())

    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())

    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())

    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())

    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())