# CAN bus configuration
CAN_INTERFACE = 'can0'         # SocketCAN interface name
CAN_BITRATE   = 500000         # Bus speed in bits per second

# CAN message ID ranges
BRAKE_ID_START = 0x200         # IDs 0x200–0x2FF reserved for brake controller
BRAKE_ID_END   = 0x2FF  
MOTOR_ID_START = 0x300         # IDs 0x300–0x3FF reserved for motor controller
MOTOR_ID_END   = 0x3FF  
LED_ID_START   = 0x400         # IDs 0x400–0x4FF reserved for LED controller
LED_ID_END     = 0x4FF  

# Heartbeat message IDs
BRAKE_HEARTBEAT_ID = 0x299     # Brake controller heartbeat 
MOTOR_HEARTBEAT_ID = 0x399     # Motor controller heartbeat 
LED_HEARTBEAT_ID   = 0x499     # LED controller heartbeat

# Braking commands
BRAKE_ENGAGE_CMD    = 0x201    # Engage pneumatic brakes
BRAKE_DISENGAGE_CMD = 0x202    # Release pneumatic brakes 

# Motor commands
MOTOR_STOP_CMD      = 0x301  
MOTOR_START_10_CMD  = 0x302  # start motors (10%)
MOTOR_START_30_CMD  = 0x303  # start motors (10%)
MOTOR_START_50_CMD  = 0x304  # start motors (50%)
MOTOR_START_70_CMD  = 0x305  # start motors (70%)
MOTOR_START_100_CMD = 0x306  # Full power command  
CRAWL_CMD = 0x310

# Timeouts
HEARTBEAT_TIMEOUT = 10         # Seconds before triggering a fault on missing heartbeat :contentReference[oaicite:11]{index=11}  

# State machine keys
STATE_FAULT    = 'fault'  
STATE_DEBUG    = 'debug'  
STATE_SAFE     = 'safe'  
STATE_READY    = 'ready'  
STATE_CRAWLING = 'crawling'  
STATE_BRAKING  = 'braking'  

DEFAULT_STATE = {               # Initial flags for each top‐level state :contentReference[oaicite:12]{index=12}  
    STATE_FAULT:    False,  
    STATE_DEBUG:    False,  
    STATE_SAFE:     True,  
    STATE_READY:    False,  
    STATE_CRAWLING: False,  
}  

DEFAULT_TRANSITIONS = {         # Valid next states for each current state :contentReference[oaicite:13]{index=13}  
    STATE_FAULT:    (STATE_DEBUG, STATE_SAFE),  
    STATE_SAFE:     (STATE_FAULT, STATE_READY, STATE_DEBUG),  
    STATE_READY:    (STATE_FAULT, STATE_DEBUG, STATE_SAFE, STATE_CRAWLING),  
    STATE_CRAWLING: (STATE_FAULT, STATE_DEBUG, STATE_BRAKING),  
    STATE_BRAKING:  (STATE_FAULT, STATE_DEBUG, STATE_SAFE),  
    STATE_DEBUG:    (STATE_FAULT, STATE_SAFE),  
}  

# GUI command constants
GUI_CMD_POD_DEBUG        = 'POD_DEBUG'  
GUI_CMD_READY_TO_LAUNCH  = 'READY_TO_LAUNCH'  
GUI_CMD_SAFE_TO_APPROACH = 'SAFE_TO_APPROACH'  
GUI_CMD_CRAWL            = 'KDAYS_CRAWLING'  
GUI_CMD_EMERGENCY_STOP   = 'EMERGENCY_STOP'  

# Sensor thresholds (placeholder values—calibrate in testing)
RSSI_THRESHOLD_DBM = -70       # dBm minimum signal strength 
HP_TEMP_THRESHOLD  = 60        # °C high‐pressure BMS overheat limit  
LP_TEMP_THRESHOLD  = 60        # °C low‐pressure BMS overheat limit  
BC_L_THRESHOLD     = 20        # Brake pressure low threshold  
BC_U_THRESHOLD     = 80        # Brake pressure high threshold  
STA_THRESHOLD      = 30        # Seconds before auto‐timeout back to Safe

# LED color map for real‐time status indicators
STATE_COLORS = {               # Used by LED controller node
    STATE_FAULT:    'RED',  
    STATE_SAFE:     'GREEN',  
    STATE_READY:    'BLUE',  
    STATE_CRAWLING: 'YELLOW',  
    STATE_BRAKING:  'ORANGE',  
    STATE_DEBUG:    'PURPLE',  
}