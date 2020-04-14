URL = "http://127.0.0.1:8083/" # Default listen port
API_KEY = "XXXXX" # Jeedom Openzwave API Key
DEFAULT_WAKEUP_INTERVAL = 86400
SKIP_MONITORING_NODE_ID = [1, 41, 37]

NODE_LAST_RECEIVED_MAX_OVERRIDE = {
    1: 86400,
    #NodeID: Time in second since last received to consider node as dead
}