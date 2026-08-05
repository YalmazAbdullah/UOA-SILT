import socket
import json
import struct
from datetime import datetime, timezone

from listeners import os_input_listener, target_listener

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000 

#MAX_PACKET_SIZE = 65535

## TEMPORARY VARIABLE 
is_recording = True

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

def main():

    state = {"server_sock": None, "target_sock": None}

    def forward_os_event(event):

        if state["server_sock"] is not None:
            server_send(state["server_sock"], event)
            
            print("\n=== OS INPUT RECEIVED ===")
            print(json.dumps(event, indent=2))

            print(f"[SERVER] Payload sent to {SERVER_HOST}:{SERVER_PORT}")

    state["server_sock"] = server_connect(SERVER_HOST, SERVER_PORT)
    state["target_sock"] = target_listener.target_connect(TARGET_HOST, TARGET_PORT)

    recorder = os_input_listener.InputRecording(on_event=forward_os_event)
    recorder.start()

    print("started recording")

    try: 
        while is_recording: 

            payload, addr = target_listener.listen(state["target_sock"])

            if payload is None:
                continue

            print("\n=== TARGET PACKET RECEIVED ===")
            print(f"From : {addr}")
            print(json.dumps(payload, indent=2))

            if state["server_sock"] is None:
                state["server_sock"] = server_connect(SERVER_HOST, SERVER_PORT)
            
            if state["server_sock"] is not None:
                if server_send(state["server_sock"], payload):
                    print(f"[SERVER] Payload sent to {SERVER_HOST}:{SERVER_PORT}")
                else:
                    print("[SERVER] Not connected, trying again.")
                    state["server_sock"].close()
                    state["server_sock"] = None

    except KeyboardInterrupt: 
        print("Stop it.")

    except Exception as e:
        print(f"[CLIENT] Error: {e}")

    finally: 
        if state["server_sock"] is not None:
            state["server_sock"].close()

        if state["target_sock"] is not None:
            state["target_sock"].close()

        recorder.stop()

if __name__ == "__main__":
    main()