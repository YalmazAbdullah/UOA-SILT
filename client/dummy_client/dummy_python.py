import socket
import json
#from datetime import datetime, timezone 

HOST = "127.0.0.1"
PORT = 5000 
APP_NAME = "place_holder"

def send_log(log):
    payload = {
        "target": APP_NAME,
        "log": log,
        #"timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    data = json.dumps(payload).encode("UTF-8")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(data, (HOST, PORT))
    except:
        pass

def main():
    send_log("Hello world")

if __name__ == "__main__":
    main() 