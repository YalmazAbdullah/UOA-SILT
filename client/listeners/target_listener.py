import socket
import json
import struct
from datetime import datetime, timezone

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000 

MAX_PACKET_SIZE = 65535

def server_connect(host, port):

    try:

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.connect((host, port))

        print(f"[SERVER] Connection successful: {host}:{port}")

        return server_sock

    except ConnectionRefusedError:

        print(f"[SERVER] Connection refused: {host}:{port}")
        print("[SERVER] Data will NOT be forwarded.")

        return None

    except OSError as e:

        print(f"[SERVER] Connection failed: {host}:{port} ==> {e}")
        print("[SERVER] Data will NOT be forwarded.")

        return None

def server_send(sock, payload):
   
    try:

        data = json.dumps(payload).encode("UTF-8")
        header = struct.pack(">I", len(data))

        sock.sendall(header + data)

        return True

    except (ConnectionResetError, OSError) as e:

        print(f"[SERVER] Data failed to send due to error: {e}")

        return False

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

def main():

    target_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    target_sock.bind((TARGET_HOST, TARGET_PORT))

    print(f"[CLIENT TO TARGET] Listening: {TARGET_HOST}:{TARGET_PORT}")

    server_sock = server_connect(SERVER_HOST, SERVER_PORT)

    try:
        while True:

            data, addr = target_sock.recvfrom(MAX_PACKET_SIZE)

            try:

                payload = json.loads(data.decode("UTF-8"))

                payload = repackage_payload(payload)

                print("\n=== TARGET PACKET RECEIVED ===")
                print(f"From : {addr}")
                print(json.dumps(payload, indent=2))

                if server_sock is not None:
                    server_send(server_sock, payload)
                    print(f"[SERVER] Payload sent to {SERVER_HOST}:{SERVER_PORT}")
                else:
                    print("[SERVER] No server connection.")

            except json.JSONDecodeError:

                print("\n=== INVALID JSON RECEIVED ===")
                print(f"From: {addr}")
                print(data)

    except KeyboardInterrupt:

        print("\n [CLIENT] Stop it.")

    finally:

        if target_sock is not None:
            target_sock.close()

        if server_sock is not None:
            server_sock.close()

if __name__ == "__main__":
    main()