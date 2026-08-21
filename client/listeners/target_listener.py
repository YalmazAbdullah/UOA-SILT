import socket
import json
from datetime import datetime, timezone

MAX_PACKET_SIZE = 65535

def target_connect(host, port):

    target_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    target_sock.bind((host, port))
    
    print(f"[CLIENT TO TARGET] Listening: {host}:{port}") 

    return target_sock

def repackage_payload(payload):

    client_time = datetime.now(timezone.utc).isoformat()

    return {
        "target_time": payload.get("target_time"),
        "client_time": client_time,
        "source": payload.get("source"),
        "target": payload.get("target"),
        "event": payload.get("event"),
        "data": payload.get("data")
    }

def listen(target_sock):
   
    try: 
        data, addr = target_sock.recvfrom(MAX_PACKET_SIZE)

        payload = json.loads(data.decode("UTF-8"))
        payload = repackage_payload(payload)

        return payload, addr

    except json.JSONDecodeError: 

        print("\n=== INVALID JSON RECEIVED ===")
        return None, None

    except OSError as e:
        print("=== SOCKET ERROR {e} ===")
        return None, None

  

    