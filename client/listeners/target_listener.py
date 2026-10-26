import socket
import json
from datetime import datetime, timezone

MAX_PACKET_SIZE = 65535
SOCKET_TIMEOUT = 0.5 # Time for the client to listen to the target's sock

def target_connect(host, port):

    target_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        target_sock.bind((host, port))
        target_sock.settimeout(SOCKET_TIMEOUT)
        
        print(f"[CLIENT TO TARGET] Listening: {host}:{port}") 

    except OSError as e:
        target_sock.close()

        print(f"[CLIENT TO TARGET] Failed to connect: {e}")

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

    except socket.timeout:
        # Uncomment this code if you need to test timeouts, otherwise
        # the terminal will be bloated in the print
        # print("[CLIENT TO TARGET]: Failed because of timeout")
        return None, None

    except json.JSONDecodeError as e: 
        print(f"[CLIENT TO TARGET]: Failed to decode: {e}")
        return None, None

    except OSError as e:
        print(f"[CLIENT TO TARGET]: Failed to listen: {e}")
        raise

    


  

    