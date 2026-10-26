import socket
import json
import struct

from listeners import os_input_listener, target_listener

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000 
SOCKET_TIMEOUT = 0.5


def receive_packets(target_sock):

    try:
        return target_listener.listen(target_sock)
    
    except socket.timeout:
        return None, None

    
def server_connect(host, port):

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server_sock.connect((host, port))

        print(f"[SERVER] Connection successful: {host}:{port}")
        return server_sock

    except ConnectionRefusedError:
        print(f"[SERVER] Connection refused: {host}:{port}")
        print("[SERVER] Data will NOT be forwarded.")
        
        return None

    except OSError as e:
        server_sock.close()

        print(f"[SERVER] Connection failed: {host}:{port} ==> {e}")
        print("[SERVER] Data will NOT be forwarded.")
        return None


def server_send(sock, payload):
    if sock is None:
        return False

    try:
        data = json.dumps(payload).encode("UTF-8")
        header = struct.pack(">I", len(data))
        sock.sendall(header + data)
        return True

    except OSError as e:
        print(f"[SERVER] Data failed to send because of an OSerror: {e}")
        return False      


def main():

    server_sock = None
    target_sock = None

    try:
        server_sock = server_connect(SERVER_HOST, SERVER_PORT)
        target_sock = target_sock = target_listener.target_connect(TARGET_HOST, TARGET_PORT)
        target_sock.settimeout(SOCKET_TIMEOUT)

        print("[CLIENT] Listening for target packets. Press Ctrl+C to stop it.")

        while True:
            payload, addr = receive_packets(target_sock)

            if payload is None:
                continue

            print("\n=== TARGET PACKET RECEIVED ===")
            print(f"From : {addr}")
            print(json.dumps(payload, indent=2))

            if server_sock is None:
                server_sock = server_connect(SERVER_HOST, SERVER_PORT)

            if server_sock is not None:
                if server_send(server_sock, payload):
                    print(f"[SERVER] Payload sent to {SERVER_HOST}:{SERVER_PORT}")         
                else:
                    server_sock.close()
                    server_sock = None
                    print("[SERVER] Disconnected")

    except KeyboardInterrupt:
        print("\n[CLIENT] Stop it.")
    
    except OSError as e:
        print(f"[CLIENT] Error involving OS: {e}") 

    finally:
        if server_sock is not None:
            server_sock.close()
            print("[CLIENT] Target socket closed.")

        if target_sock is not None:
            target_sock.close()
            print("[CLIENT] Server socket closed.")
           

if __name__ == "__main__":
    main()