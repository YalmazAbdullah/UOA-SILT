import socket
import json
from datetime import datetime, timezone 

HOST = "127.0.0.1"
PORT = 5000 

def send_log(log):

    payload = {
        "target_time": datetime.now(timezone.utc).isoformat(),
        "source": "target",
        "target": "pytest",
        "event": "sending_log_python",
        "data": {'message': log}
    }
    
    data = json.dumps(payload).encode("UTF-8")

    try:

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(data, (HOST, PORT))

    except Exception as e:
        print(f"Failed to send UDP packet: {e}")

def main():
    send_log("Hello world")

if __name__ == "__main__":
    main() 