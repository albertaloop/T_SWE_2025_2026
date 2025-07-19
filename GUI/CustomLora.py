import time
from pySX127x.SX127x.LoRa import *
from pySX127x.SX127x.board_config import BOARD
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from utils.formatPayload import unpackPayload, convertStringToByteList, PodMessage
from config import *

class CustomLora(LoRa, QObject):
    state_updated = pyqtSignal(str)  # the new state will be emitted here

    def __init__(self, verbose=False):
        LoRa.__init__(self, verbose)
        QObject.__init__(self) 
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.connected = False
        self.current_message = PodMessage()

        # Timer for connection timeout
        self.connection_timer = QTimer()
        self.connection_timer.setSingleShot(True)
        self.connection_timer.timeout.connect(self.handle_connection_timeout)

    def on_rx_done(self):
        BOARD.led_on()
        print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        new_msg = unpackPayload(payload)

        self.current_message = new_msg
        print("Received:", new_msg)

        if (new_msg.fsm_state == CONNECTION_MESSAGE):
            print("Connected to server")
            self.connected = True
            self.connection_timer.stop()

        self.state_updated.emit(new_msg.fsm_state)
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

    def start(self):          
        print ("Checking connection")
        self.connection_timer.start(5000)
        self.write_payload(convertStringToByteList(CONNECTION_MESSAGE))
        self.set_mode(MODE.TX)
        time.sleep(0.1)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
    
    def handle_connection_timeout(self):
        print("Connection timeout: did not receive CONNECTION_MESSAGE in 5 seconds.")