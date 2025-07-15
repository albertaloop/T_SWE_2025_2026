from CustomLora import *

class Command:
    def __init__(self, message, receiver, ack_msg):
        self.message = message
        self.ack_msg = ack_msg
        self.receiver = receiver
    def execute(self, command_requested, cmd_lock):
        print(self.message)
        # while True:
        self.receiver.write_payload(self.message)
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
        self.message = [0x310]

class EStop(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self.message = [0x20]

# Not using for K-Days
class Launch(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self.message = [0xC0, 0xC4]

class PrepareLaunch(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        amsg = [0xA0, 0xA2]
        self.message = [0xC0, 0xC2]
        self.ack_msg = bytes(amsg)

