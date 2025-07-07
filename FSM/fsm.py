

import can
import rospy
import py_trees
from std_msgs.msg import String # message type
from pynput import keyboard
import time




# CANbus
CANBUS = can.interface.Bus(interface='socketcan', channel='can0', bitrate = 500000) # bitrate = ??????


# --- Global State ---
DEFAULT_STATE = {
   'fault': False,
   'safe': True,
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


# --- Time since last heartbeat signal ---
signal_time_elasped = {
   'brakes': 0,
   'motor': 0,
   'LED': 0
}




state = DEFAULT_STATE


   


# --- Keyboard Listener ---
def on_press(key):
   try:
       if key.char == 'f':
           state['fault'] = not state['fault']
           print(f"Toggle FAULT: {state['fault']}")
       elif key.char == 'd':
           state['debug'] = not state['debug']
           print(f"Toggle DEBUG: {state['debug']}")
       elif key.char == 's':
           state['safe'] = not state['safe']
           print(f"Toggle SAFE: {state['safe']}")
       elif key.char == 'r':
           state['ready'] = not state['ready']
           print(f"Toggle READY: {state['ready']}")
       elif key.char == 'c':
           state['crawling'] = not state['crawling']
           print(f"Toggle CRAWLING: {state['crawling']}")
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
       print("Handling fault...")
       return py_trees.common.Status.SUCCESS




class RunDiagnostics(py_trees.behaviour.Behaviour):
   def update(self):
       print("Running diagnostics...")
       return py_trees.common.Status.SUCCESS
 
class SafeToApproach(py_trees.behaviour.Behaviour):
   def update(self):
       if not check_ready():
           print("Pod is safe to approach...")
           return py_trees.common.Status.RUNNING




       return py_trees.common.Status.SUCCESS
     
class ReadyToRun(py_trees.behaviour.Behaviour):
   def update(self):
       if not check_crawling():
           print("Ready to run, waiting for crawl command...")
           return py_trees.common.Status.RUNNING
     
       return py_trees.common.Status.SUCCESS


class ExecuteCrawling(py_trees.behaviour.Behaviour):
   # --- Execute crawling for max_attempt_count ticks ---
   def __init__(self, name, max_attempt_count=1):
       super(ExecuteCrawling, self).__init__(name)
       self.max_attempt_count = max_attempt_count
       self.attempt_count = max_attempt_count




   def initialise(self):
       self.attempt_count = self.max_attempt_count
 
   def update(self):
       self.attempt_count -= 1
       print("Executing crawling behavior...")
       if not self.attempt_count:
           state['crawling'] = False
           return py_trees.common.Status.SUCCESS




       return py_trees.common.Status.RUNNING




class ExecuteBraking(py_trees.behaviour.Behaviour):
   def update(self):
       print("Executing braking behavior...")
       return py_trees.common.Status.SUCCESS
   


class SubscriberBehavior(py_trees.behaviour.Behaviour):
   
    def __init__(self, name = "CANSubscriber", node_name= "can_messages", msg_type= String):
        """
        Initializes the behaviour
        """
        super().__init__(name=name)
        self.node_name = node_name
        self.msg_type = msg_type
        self.last_msg = None
        self.subscriber = None
        
        print("subscriber initializtion complete")


    def setup(self):
        """
        Initializes the subscriber
        """
        print("in setup")
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
        print("last message updated")

    def update(self):
        """
        Check for new messages
        """
        print("in update")
        if self.last_msg is not None:
            print("try read_message")
            result = read_message(self.last_msg)
            self.last_msg = None  # clear the message
            print("read success")
            return py_trees.common.Status.SUCCESS
        print("subscriber running")
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
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS




def read_message(msg):
    """
    Read an incoming message, add logs for each possible message (if needed), change state (if needed)
    msg: 11 total bits — bits 0-7 --> message, bits 8 - 10 --> identifier
    """

    print("READING MESSAGE")

    try:
        # Convert ROS String to integer
        msg = int(msg.data, 16)  # Assuming message is in hex format
    except ValueError:
        rospy.logwarn(f"Invalid CAN message format: {msg.data}")
        return
   


    if msg >= 0x200 and msg <= 0x2FF :
        if msg & 0x0FF == 0x001 :
            # Engage brakes, set GPIOs to low
            change_state('braking')
        if msg & 0x0FF == 0x000 :
            # Disengage brakes, set GPIOs to high
            change_state('safe')
        if msg & 0x0FF == 0x099 :
            signal_time_elasped['brakes'] = 0
    elif msg >= 0x300 and msg <= 0x4FF :
        if msg & 0x0FF == 0x001 :
            # Stop motors
            change_state('safe')
        if msg & 0x0FF == 0x002 :
            # start motors (10%)
            change_state('crawling')
        if msg & 0x0FF == 0x003 :
            # start motors (30%)
            change_state('crawling')
        if msg & 0x0FF == 0x004 :
            # start motors (50%)
            change_state('crawling')
        if msg & 0x0FF == 0x005 :
            # start motors (70%)
            change_state('crawling')
        if msg & 0x0FF == 0x006 :
            # start motors (100%)
            change_state('crawling')
        if msg & 0x0FF == 0x099 :
            signal_time_elasped['motor'] = 0
    elif msg >= 0x400 and msg <= 0x4FF :
        if msg & 0x0FF == 0x099 :
            signal_time_elasped['LED'] = 0
        else :
            count = 0x401
            current = current_state()
            for key in list(state.keys()) :
                if current == key :
                    break
                count += 0x001
            msg = count


    # Probably need to make separate function later
    response = can.Message(
        arbitration_id=msg,
        data=[0x00, 0x00, 0x00, 0x00],  # data
    )
    try:
        CANBUS.send(response)
        print(f"Message sent: {response}")
    except can.CanError:
        print(f"Message FAILED to send: {response}")




def check_signals() :
    unresponsive = []
    for key in list(signal_time_elasped.keys()) :
        if signal_time_elasped[key] >= 10 :
            print(f"{key} has not responded in {signal_time_elasped[key]} seconds!\n Entering fault state.")
            change_state('fault')
            unresponsive.append(key)
        signal_time_elasped[key] += 1  
    return unresponsive if unresponsive else None


       






# --- Build Behavior Tree ---
def create_behavior_tree():
   root = py_trees.composites.Selector("Root Selector", memory=False) # Memory false makes sure that the children are re-evaluated for each tick (useful for when state changes)


   # parallel monitor for running subscriber and signal checks
   monitor = py_trees.composites.Parallel("Monitoring", policy=py_trees.common.ParallelPolicy.SuccessOnAll())


   can_subscriber = SubscriberBehavior("CANSubscriber", "can_messages", String)
   print("Subscriber behaviour added")
   signal_checker = CheckSignals()
   
   monitor.add_children([can_subscriber, signal_checker])


   state_machine = py_trees.composites.Selector("State Machine", memory=False)


   fault_seq = py_trees.composites.Sequence("Fault Sequence", memory=False)
   fault_seq.add_children([InFault(name="Check fault"), HandleFault(name="Handle fault")])




   debug_seq = py_trees.composites.Sequence("Debug Sequence", memory=False)
   debug_seq.add_children([InDebug(name="Check debug"), RunDiagnostics(name="Run diagnostics")])




   normal_seq = py_trees.composites.Sequence("Normal Operation Sequence", memory=False)




   safe_seq = py_trees.composites.Sequence("Safe Sequence", memory=False)
   safe_seq.add_children([
       InSafeToApproach(name="Check safe"),
       SafeToApproach(name="Safe to approach")
   ])




   ready_seq = py_trees.composites.Sequence("Ready Sequence", memory=False)
   ready_seq.add_children([
       InReadyToRun(name="Check ready"),
       ReadyToRun(name="Ready to run")
   ])




   main_seq = py_trees.composites.Sequence("Main Sequence", memory=False)
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
    start_keyboard_listener()
   
    tree = py_trees.trees.BehaviourTree(create_behavior_tree())
  
    tree.setup()
    print("tree setup")

    try:
        rate = rospy.Rate(1)
        while not rospy.is_shutdown():
            tree.tick()
            rate.sleep()
           
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        CANBUS.shutdown()
