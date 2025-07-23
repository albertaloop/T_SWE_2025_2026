# import sys
# sys.path.append("/home/veerparasmehra/T_SWE_2025_2026") 
import time
from pySX127x.SX127x.LoRa import *
from pySX127x.SX127x.board_config import BOARD
from PyQt5.QtCore import QObject, pyqtSignal
from utils.formatPayload import unpackPayload, convertStringToByteList, PodMessage, convertByteListToString
from config import *
# import threading

class CustomLora(LoRa, QObject):
    state_updated = pyqtSignal(PodMessage)  # the new state will be emitted here

    def __init__(self, verbose=False):
        LoRa.__init__(self, verbose)
        QObject.__init__(self) 
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.connected = False
        self.timedOut = False
        self.current_message = PodMessage()

        # Timer for connection timeout
        # self.timer = threading.Timer(10.0, self.handleConnectionTimeout)

    def on_rx_done(self):
        BOARD.led_on()
        print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        if not (self.connected):
            str_payload = convertByteListToString(payload)
            print(f"String payload: {str_payload}")
            if (str_payload == CONNECTION_MESSAGE):
                print("Connected to server, starting client")
                self.connected = True
                # self.timer.cancel()
            else:
                BOARD.led_off()
            return

        new_msg = unpackPayload(payload)

        self.current_message = new_msg
        print("Received:", new_msg)
        self.state_updated.emit(new_msg)
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
        # self.timer.start()
        while not (self.connected):       
            self.write_payload(convertStringToByteList(CONNECTION_MESSAGE))
            print ("Checking connection")
            self.set_mode(MODE.TX)
            time.sleep(2)
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)
            start_time = time.time()
            while (time.time() - start_time < 10): # Check for connection every 10 seconds
                pass

        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT) # Receiver mode
        time.sleep(2)
    
    # def handleConnectionTimeout(self):
    #     print("Connection timeout: did not receive CONNECTION_MESSAGE within 10 seconds.")
    #     self.timedOut = True
