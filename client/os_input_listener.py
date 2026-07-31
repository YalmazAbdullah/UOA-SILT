import socket
import json
from datetime import datetime, timezone 
from pynput import mouse, keyboard

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000 

class InputRecording:
    def __init__(self) -> None:
        self.mouse_events = []
        self.keyboard_events = []

    def on_click(self, x, y , mouse_button, is_pressed):
        if is_pressed:
            client_time = get_client_time()
            self.mouse_events.append([client_time, x, y, mouse_button])

    def on_press(self, key):
        client_time = get_client_time()

        try: 
            self.keyboard_events.append([client_time, key.char])
        except AttributeError:
            self.keyboard_events.append([client_time, key])

    def on_release(self, key):
        client_time = get_client_time()
        if key == keyboard.Key.esc:
            self.keyboard_events.append([client_time, key])
            return False

def get_client_time():
    return datetime.now(timezone.utc).isoformat()

def send_log(log):

    payload = {
        "client_time": datetime.now(timezone.utc).isoformat(),
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
    recorder = InputRecording()

    mouse_listener = mouse.Listener(on_click=recorder.on_click)
    keyboard_listener = keyboard.Listener(on_press=recorder.on_press, on_release=recorder.on_release)

    mouse_listener.start()
    keyboard_listener.start()

    keyboard_listener.join()
    mouse_listener.stop()


if __name__ == "__main__":
    main() 