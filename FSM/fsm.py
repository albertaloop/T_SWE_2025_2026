import os
import sys
import can
import rospy
import py_trees
from std_msgs.msg import String # message type
from pynput import keyboard
from datetime import datetime
from py_trees.common import ParallelPolicy




# CANbus
CANBUS = can.interface.Bus(interface='socketcan', channel='can0', bitrate = 250000)


# --- Global State ---
DEFAULT_STATE = {
   'fault': True,
   'safe': False,
   'ready': False,
   'crawling': False,
   'braking' : False,
   'debug': False
}


# --- Possible transitions (including GUI commands) ---
DEFAULT_TRANSITIONS = {
   'fault': ('debug', 'safe'),
   'safe': ('fault', 'ready', 'debug'),
   'ready': ('fault', 'debug', 'safe', 'crawling'),
   'crawling': ('fault', 'debug', 'braking'),
   'braking' : ('fault', 'debug', 'safe'),
   'debug': ('fault', 'safe')
}


DEFAULT_MESSAGES = {
    'ENGAGE_BRAKES' : 0x201 ,
    'DISENGAGE_BRAKES' : 0x202,
    'MOTOR_CRAWLING' : 0x300,
    'STOP_MOTOR' : 0x301,
    'MOTOR_10%' : 0x302,
    'MOTOR_30%' : 0x303,
    'MOTOR_50%' : 0x304,
    'MOTOR_70%' : 0x305,
    'MOTOR_100%' : 0x306,
    'MOTOR_REVERSE' : 0x307,
    'MOTOR_CRAWL' : 0x308,
    'LED_FAULT' : 0x401,
    'LED_SAFE' : 0x402,
    'LED_READY' : 0x403,
    'LED_CRAWLING' : 0x404,
    'LED_BRAKING' : 0x405,
    'LED_DEBUG' : 0x406
}


# --- Time since last heartbeat signal ---
signal_time_elasped = {
   'brakes': 0,
   'motor': 0,
   'LED': 0,
   'LORA' : 0
}

# --- Global State ---
state = DEFAULT_STATE

# --- Keyboard Listener ---
def on_press(key):
   try:
       if key.char == 'f' and not state['fault'] :
           change_state('fault')
           #print(f"Toggle FAULT: {state['fault']}")
       elif key.char == 'd' and not state['debug'] and check_signals() :
           change_state('debug')
           #print(f"Toggle DEBUG: {state['debug']}")
       elif key.char == 's' and not state['safe'] and check_signals() :
           change_state('safe')
           #print(f"Toggle SAFE: {state['safe']}")
       elif key.char == 'r' and not state['ready'] and check_signals() :
           change_state('ready')
           #print(f"Toggle READY: {state['ready']}")
       elif key.char == 'c' and not state['crawling'] and check_signals() :
           change_state('crawling')
           #print(f"Toggle CRAWLING: {state['crawling']}")
       elif key.char == 'b' and not state['braking'] and check_signals() :
           change_state('braking')
           #print(f"Toggle BRAKING: {state['braking']}")

   except AttributeError:
       pass  # special keys ignored




def start_keyboard_listener():
   listener = keyboard.Listener(on_press=on_press)
   listener.start()




# --- State functions ---
def check_fault(): return state['fault']
def check_debug(): return state['debug']    
def check_safe(): return state['safe']
def check_ready(): return state['ready']
def check_crawling(): return state['crawling']
def check_braking(): return state['braking']


def current_state() :
    for key in list(state.keys()) :
        if state[key] :
           return key
       
def change_state(next_state):
    current = current_state()
    if current is None:
        print("State is none.")
        return False
    elif next_state in DEFAULT_TRANSITIONS[current]:
        state[current] = False
        state[next_state] = True
        print(f"State changed from {current} to {next_state}")
        return True
    else:
        print(f"Error: Cannot transition from {current} to {next_state}")
        return False



# --- Conditions ---
class InFault(py_trees.behaviour.Behaviour):
   def update(self):
       return py_trees.common.Status.SUCCESS if check_fault() else py_trees.common.Status.FAILURE




class InDebug(py_trees.behaviour.Behaviour):
   def update(self):
       return py_trees.common.Status.SUCCESS if check_debug() else py_trees.common.Status.FAILURE




class InSafeToApproach(py_trees.behaviour.Behaviour):
   def update(self):
       return py_trees.common.Status.SUCCESS if check_safe() else py_trees.common.Status.FAILURE




class InReadyToRun(py_trees.behaviour.Behaviour):
   def update(self):
       return py_trees.common.Status.SUCCESS if check_ready() else py_trees.common.Status.FAILURE




class InCrawling(py_trees.behaviour.Behaviour):
   def update(self):
       return py_trees.common.Status.SUCCESS if check_crawling() else py_trees.common.Status.FAILURE
   
class InBraking(py_trees.behaviour.Behaviour):
   def update(self):
       return py_trees.common.Status.SUCCESS if check_braking() else py_trees.common.Status.FAILURE




# --- Actions ---
class HandleFault(py_trees.behaviour.Behaviour):
   def update(self):
        print("State is FAULT. Running operations...")
        safe = send_message(DEFAULT_MESSAGES['ENGAGE_BRAKES']) and send_message(DEFAULT_MESSAGES['STOP_MOTOR']) and send_message(DEFAULT_MESSAGES['LED_FAULT'])
        if safe and check_signals() :
            print('Fault operations successful. Changing state to SAFE...')
            change_state('safe')
            return py_trees.common.Status.SUCCESS
        else :
            print('Failed to complete fault operations. Will remain in FAULT state.')
        return py_trees.common.Status.RUNNING
       

# TODO --- Debug operations
class RunDiagnostics(py_trees.behaviour.Behaviour):
   def update(self):
       print("Running diagnostics...")
       print("Debug unavailable")
       change_state('fault')
       return py_trees.common.Status.SUCCESS
 

class SafeToApproach(py_trees.behaviour.Behaviour):
   def __init__(self, name, max_attempt_count = 1) :
       super(SafeToApproach, self).__init__(name)
       self.max_attempt_count = max_attempt_count
       self.attempt_count = max_attempt_count

   def initialise(self):
       self.attempt_count = self.max_attempt_count

   def update(self):
       if not check_signals() :
           return py_trees.common.Status.FAILURE
       if check_safe() :
           print("State is SAFE. Running operations...")
           if self.attempt_count :  
                self.attempt_count -= 1
                safe = send_message(DEFAULT_MESSAGES['ENGAGE_BRAKES']) and send_message(DEFAULT_MESSAGES['STOP_MOTOR']) and send_message(DEFAULT_MESSAGES['LED_SAFE'])
                if safe:
                        print('Operations successful — pod is safe to approach. Will remain in SAFE state until given command or error occurs.')
                else :
                        print('Operations unsuccessful. Changing state to FAULT...')
                        change_state('fault')
                        return py_trees.common.Status.FAILURE
           else :
               print('Max SAFE state operations have been reached. Will remain idle until given command or error occurs.')
       else :
           return py_trees.common.Status.SUCCESS
       return py_trees.common.Status.RUNNING
     

class ReadyToRun(py_trees.behaviour.Behaviour):
   def __init__(self, name, max_attempt_count = 1) :
       super(ReadyToRun, self).__init__(name)
       self.max_attempt_count = max_attempt_count
       self.attempt_count = max_attempt_count

   def initialise(self):
       self.attempt_count = self.max_attempt_count

   def update(self):
       if not check_signals() :
           return py_trees.common.Status.FAILURE
       if self.attempt_count <= -10 :
           print("No command recieved, returning to safe.")
           change_state('safe')
           return py_trees.common.Status.FAILURE
       if check_ready():
           print("State is READY. Running operations...")
           if self.attempt_count :
                self.attempt_count -= 1
                safe = send_message(DEFAULT_MESSAGES['DISENGAGE_BRAKES']) and send_message(DEFAULT_MESSAGES['STOP_MOTOR']) and send_message(DEFAULT_MESSAGES['LED_READY'])
                if safe :
                        print('Operations successful — pod is ready to run. Will remain in READY state until given command or error occurs.')
                else :
                        print('Operations unsuccessful. Changing state to FAULT...')
                        change_state('fault')
                        return py_trees.common.Status.FAILURE
           else :
               print('Max READY state operations have been reached. Will remain idle until given command or error occurs.')
       else :
           return py_trees.common.Status.SUCCESS
       return py_trees.common.Status.RUNNING


class ExecuteCrawling(py_trees.behaviour.Behaviour):
   # --- Execute crawling for max_attempt_count ticks ---
   def __init__(self, name, max_attempt_count=1):
       super(ExecuteCrawling, self).__init__(name)
       self.max_attempt_count = max_attempt_count
       self.attempt_count = max_attempt_count

   def initialise(self):
       self.attempt_count = self.max_attempt_count
 
   def update(self):
        if not check_signals() :
            return py_trees.common.Status.FAILURE
        if not check_crawling() :
            return py_trees.common.Status.SUCCESS
        print("State is CRAWLING. Running operations...")
        if self.attempt_count :
            self.attempt_count -= 1
            safe = send_message(DEFAULT_MESSAGES['DISENGAGE_BRAKES']) and send_message(DEFAULT_MESSAGES['MOTOR_CRAWL']) and send_message(DEFAULT_MESSAGES['LED_CRAWLING'])
            if safe and check_signals() :
                    print('Operations successful — pod is crawling. Will remain in CRAWLING state until given command or error occurs.')
            else :
                    print('Operations unsuccessful. Changing state to FAULT...')
                    change_state('fault')
                    return py_trees.common.Status.FAILURE
        else :
            print('Max CRAWLING state operations have been reached. Will remain idle until given command or error occurs.')
        return py_trees.common.Status.RUNNING


# TODO --- Braking operations
class ExecuteBraking(py_trees.behaviour.Behaviour):
   def update(self):
       print("Executing braking behavior...")
       print("Braking state unavailable, will brake in fault.")
       change_state('fault')
       return py_trees.common.Status.SUCCESS
   


class SubscriberBehavior(py_trees.behaviour.Behaviour):
   
    def __init__(self, name = "CANSubscriber", node_name= "can_messages", msg_type = String):
        """
        Initializes the behaviour
        """
        super().__init__(name=name)
        self.node_name = node_name
        self.msg_type = msg_type
        self.last_msg = None
        self.subscriber = None
    


    def setup(self):
        """
        Initializes the subscriber
        """
        self.subscriber = rospy.Subscriber(
            self.node_name,
            self.msg_type,
            self.callback
        )
        return True


    def callback(self, msg):
        """
        Updates the message in the behaviour when a new one is recieved
        """
        self.last_msg = msg

    def update(self):
        """
        Check for new messages
        """
        if self.last_msg is not None:
            read_message(self.last_msg)
            self.last_msg = None  # clear the message
        return py_trees.common.Status.RUNNING




class CheckSignals(py_trees.behaviour.Behaviour):
    """
    Check heartbeat signals
    """
    def __init__(self, name="Check Signals"):
        super(CheckSignals, self).__init__(name)
       
    def update(self):
        unresponsive = check_signals()
        if unresponsive:
            change_state('fault')
        return py_trees.common.Status.RUNNING




def read_message(msg):
    """
    Read an incoming message, add logs for each possible message (if needed), change state (if needed)
    msg: 11 total bits — bits 0-7 --> message, bits 8 - 10 --> identifier
    """

    try:
        # Convert ROS String to integer
        msg = int(msg.data, 16)  # Assuming message is in hex format
    except ValueError:
        rospy.logwarn(f"Invalid CAN message format: {msg.data}")
        return
   
    if msg >= 0x200 and msg <= 0x2FF :
        if msg & 0x0FF == 0x001 :
            # Engage brakes, set GPIOs to low
            change_state('safe')
        if msg & 0x0FF == 0x000 :
            # Disengage brakes, set GPIOs to high
            change_state('ready')
        if msg & 0x0FF == 0x099 :
            signal_time_elasped['brakes'] = datetime.now()
    elif msg >= 0x300 and msg <= 0x4FF :
        if msg & 0x0FF == 0x000 :
            # start motors (100%)
            if state['crawling'] :
                send_message('MOTOR_CRAWLING')
        if msg & 0x0FF == 0x001 :
            # Stop motors
            change_state('safe')
        if msg & 0x0FF == 0x002 :
            # start motors (10%)
            if state['crawling'] :
                send_message('MOTOR_10%')
        if msg & 0x0FF == 0x003 :
            # start motors (30%)
            if state['crawling'] :
                send_message('MOTOR_30%')
        if msg & 0x0FF == 0x004 :
            # start motors (50%)
            if state['crawling'] :
                send_message('MOTOR_50%')
        if msg & 0x0FF == 0x005 :
            # start motors (70%)
            if state['crawling'] :
                send_message('MOTOR_70%')
        if msg & 0x0FF == 0x006 :
            # start motors (100%)
            if state['crawling'] :
                send_message('MOTOR_100%')
        if msg & 0x0FF == 0x007 :
            # start motors (100%)
            if state['crawling'] :
                send_message('MOTOR_REVERSE')
        if msg & 0x0FF == 0x008 :
            # start motors (100%)
            if state['crawling'] :
                send_message('MOTOR_CRAWL')
        if msg & 0x0FF == 0x099 :
            signal_time_elasped['motor'] = datetime.now()
    elif msg >= 0x400 and msg <= 0x4FF :
        if msg & 0x0FF == 0x099 :
            signal_time_elasped['LED'] = datetime.now()
    # LORA heartbeat signal??
    signal_time_elasped['LORA'] = datetime.now()

    send_message(msg)



def send_message(msg) :

    response = can.Message(
        arbitration_id=msg,
        data=[0x00, 0x00, 0x00, 0x00],  # data
    )

    try:
        CANBUS.send(response)
        print(f"Message sent: {response}")
        return True
    except can.CanError:
        print(f"FAILED to send message: {response}")
        return False


def check_signals(logs = True) :
    responsive = True
    for key in list(signal_time_elasped.keys()) :
        time_elasped = (datetime.now() - signal_time_elasped[key]).total_seconds()
        if time_elasped > 5 or (key == 'LORA' and time_elasped > 2) :
            if not state['fault'] :
                if logs :
                    print(f"{key} has not responded in {time_elasped} seconds!\n Entering fault state.")
                change_state('fault')
            elif logs :
                print(f"{key} has not responded in {time_elasped} seconds!\n Remaining in fault state.") 
            responsive = False
    return responsive


       
# --- Build Behavior Tree ---
def create_behavior_tree():
   root = py_trees.composites.Parallel("Root", policy=ParallelPolicy.SuccessOnAll(synchronise = False))


   # parallel monitor for running subscriber and signal checks
   monitor = py_trees.composites.Parallel("Monitoring", policy=ParallelPolicy.SuccessOnAll())


   brakes_subscriber = SubscriberBehavior("brakes", "brakes", String)
   motor_subscriber = SubscriberBehavior("motor", "motor", String)
   LED_subscriber = SubscriberBehavior("LED", "LED", String)
   LORA_subscriber = SubscriberBehavior("LORA", "LORA", String)

   signal_checker = CheckSignals()
   
   monitor.add_children([brakes_subscriber, motor_subscriber, LED_subscriber, LORA_subscriber])


   state_machine = py_trees.composites.Selector("State Machine", memory = False)


   fault_seq = py_trees.composites.Sequence("Fault Sequence", memory=False)
   fault_seq.add_children([InFault(name="Check fault"), HandleFault(name="Handle fault")])




   debug_seq = py_trees.composites.Sequence("Debug Sequence", memory=False)
   debug_seq.add_children([InDebug(name="Check debug"), RunDiagnostics(name="Run diagnostics")])




   normal_seq = py_trees.composites.Sequence("Normal Operation Sequence", memory=True)




   safe_seq = py_trees.composites.Sequence("Safe Sequence", memory=True)
   safe_seq.add_children([
       InSafeToApproach(name="Check safe"),
       SafeToApproach(name="Safe to approach")
   ])




   ready_seq = py_trees.composites.Sequence("Ready Sequence", memory=True)
   ready_seq.add_children([
       InReadyToRun(name="Check ready"),
       ReadyToRun(name="Ready to run")
   ])




   main_seq = py_trees.composites.Sequence("Main Sequence", memory=True)
   main_seq.add_children([
       InCrawling(name="Check Crawling"),
       ExecuteCrawling(name="Crawling", max_attempt_count=5),
       ExecuteBraking(name="Braking")
   ])


   
   normal_seq.add_children([safe_seq, ready_seq, main_seq])


   state_machine.add_children([fault_seq, debug_seq, normal_seq])
   
   root.add_children([monitor, state_machine])


   return root




# --- Main Loop ---
if __name__ == '__main__':
    rospy.init_node('pod_state_machine', anonymous=True)

    initialized = None

    while not initialized or initialized.data != b'Aloop' :
        initialized = CANBUS.recv()
        print(f"Recieved message: {initialized.data}")
        print('Initialization message not recieved. Please send "Aloop".')

    print('Message recieved! Starting FSM.')
    
    start_keyboard_listener()
   
    tree = py_trees.trees.BehaviourTree(create_behavior_tree())
    print("Tree initialized.")

    dt = datetime.now()
    signal_time_elasped['brakes'] = dt
    signal_time_elasped['motor'] = dt
    signal_time_elasped['LED'] = dt
    signal_time_elasped['LORA'] = dt
  
    tree.setup()
    print("Tree set up. Beginning tree ticks.")

    try:
        rate = rospy.Rate(1)
        while not rospy.is_shutdown():
            tree.tick()
            rate.sleep()
           
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        CANBUS.shutdown()
