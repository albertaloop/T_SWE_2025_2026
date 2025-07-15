# Formats 2 byte payload to a list
def splitPayload(payload):
  return [(payload >> 8) & 0xFF, payload & 0xFF]

def reconstructPayload(payload):
  return (payload[0] << 8) | payload[1]