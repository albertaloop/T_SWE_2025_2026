# Formats 2 byte payload to a list
def splitPayload(payload):
  return [(payload >> 8) & 0xFF, payload & 0xFF]

def reconstructPayload(payload):
  return (payload[0] << 8) | payload[1]

# Converts string to list of 2 byte items suitable for lora
def convertStringToByteList(string):
  return [ord(c) for c in string]

def convertByteListToString(list):
  return bytes(list).decode("utf-8",'ignore')
