import py_trees
from pynput import keyboard
import time


# --- Global State ---
DEFAULT_STATE = {
   'fault': False,
   'debug': False,
   'safe': True,
   'ready': False,
   'crawling': False,
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


# --- Check functions ---
def check_fault(): return state['fault']
def check_debug(): return state['debug']
def check_safe(): return state['safe']
def check_ready(): return state['ready']
def check_crawling(): return state['crawling']


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


# --- Build Behavior Tree ---
def create_behavior_tree():
   root = py_trees.composites.Selector("Root Selector", memory=False) # Memory false makes sure that the children are re-evaluated for each tick (useful for when state changes)


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


   root.add_children([fault_seq, debug_seq, normal_seq])
   return root


# --- Main Loop ---
if __name__ == '__main__':
   start_keyboard_listener()
   tree = py_trees.trees.BehaviourTree(create_behavior_tree())
   # py_trees.display.render_dot_tree(tree.root, name="btree") # Downloads behaviour tree diagrams


   print("\nPress [f/d/s/r/c/b] to toggle states. CTRL+C to exit.\n")
   try:
       while True:
           tree.tick()
           time.sleep(1.0)  # Tick every second
   except KeyboardInterrupt:
       print("\nShutting down...")
