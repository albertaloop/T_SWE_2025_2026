from CustomLora import *
from config import *
from utils.formatPayload import convertStringToByteList, packPayload
from time import sleep

class Command:
    def __init__(self, message, receiver: CustomLora):
        self.message = message
        self.receiver = receiver
    def execute(self, command_requested, cmd_lock):
        self.receiver.current_message.gui_command = self.message

        # Mock
        self.receiver.read_payload = lambda nocheck=True: packPayload(self.receiver.current_message)
        
        print("Sending: ", self.receiver.current_message)
        self.receiver.write_payload(list(packPayload(self.receiver.current_message)))
        self.receiver.set_mode(MODE.TX)
        sleep(0.5)
        self.receiver.reset_ptr_rx()
        self.receiver.set_mode(MODE.RXCONT)
        with cmd_lock:
            command_requested[0] = "none"
        print("Execution complete")
        
        # Mock calling the received func
        self.receiver.on_rx_done()

class Crawl(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self.message = STATE_CRAWLING

class EStop(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self.message = STATE_FAULT

# Not using for K-Days
# class Launch(Command):
#     def __init__(self, receiver):
#         self.receiver = receiver
#         self.message = [0xC0, 0xC4]

class PrepareLaunch(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self.message = STATE_READY

