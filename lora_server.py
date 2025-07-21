#!/usr/bin/env python3

""" This program asks a client for data and waits for the response, then sends an ACK. """

# Copyright 2018 Rui Silva.
#
# This file is part of rpsreal/pySX127x, fork of mayeranalytics/pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.

import time
from SX127x.LoRa import *
#from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
from utils.formatPayload import unpackPayload, convertStringToByteList, PodMessage, convertByteListToString
from config import *

BOARD.setup()
BOARD.reset()
#parser = LoRaArgumentParser("Lora tester")


class mylora(LoRa):
    def __init__(self, verbose=False):
        super(mylora, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.var=0
        self.connected = False

    def on_rx_done(self):
        BOARD.led_on()
        #print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        #print(bytes(payload).decode("utf-8",'ignore')) # Receive DATA
        print(f"Recieved: {payload}")
        str_payload = convertByteListToString(payload)
        print(f"String Payload: {str_payload}")
        if not self.connected:
            if (str_payload == CONNECTION_MESSAGE):
                self.connected = True
                print("Connected to server")
                print ("Send: ACK")
                time.sleep(2) # Wait for the client be ready
                self.write_payload(convertStringToByteList(CONNECTION_MESSAGE))
                self.set_mode(MODE.TX)
            elif (not self.connected):
                BOARD.led_off()
                return
        unpacked_payload = unpackPayload(payload)
        print(f"Unpacked Payload: {unpacked_payload}")
        BOARD.led_off()
        #time.sleep(1) # Wait for the client be ready
        #self.write_payload([255, 255, 0, 0, 65, 67, 75, 0]) # Send ACK
        #self.set_mode(MODE.TX)
        #self.var=1
        time.sleep(2)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

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
        while True:
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT) # Receiver mode
            while True:
                pass;

    '''
    def start(self):
        #self.reset_ptr_rx()
        #self.set_mode(MODE.RXCONT) # Receiver mode
        while True:       
            while (self.var==0):
                #print ("Send: INF")
                self.write_payload([255, 255, 0, 0, 73, 78, 70, 0]) # Send INF
                self.set_mode(MODE.TX)
                time.sleep(2) # there must be a better solution but sleep() works
                self.reset_ptr_rx()
                self.set_mode(MODE.RXCONT) # Receiver mode
            
                start_time = time.time()
                while (time.time() - start_time < 10): # wait until receive data or 10s
                    pass;
                    
            self.var=0
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT) # Receiver mode
            time.sleep(2)
            '''