import socket
import json
import time
from datetime import datetime, timezone 
from pynput import mouse, keyboard


TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000 

class InputRecording:
    def __init__(self) -> None:
        self.os_input_events = []

    def on_click(self, x, y , mouse_button, is_pressed):

    

        if is_pressed:
            event_name = "mouse_event"
            client_time = get_client_time()
            coordinates = (f"x-pos: {x}, y-pos: {y}")
            self.os_input_events.append([client_time, "client", event_name, coordinates, mouse_button])

    def on_press(self, key):

        client_time = get_client_time()

        try:  
            event_name = f"keyboard_pressed_{key.char}"
            self.os_input_events.append([client_time, "client", event_name])
        except AttributeError:
            event_name = f"keyboard_pressed_{key}"
            self.os_input_events.append([client_time, "client", event_name])

    def on_release(self, key):
        """ temporary function that should be moved onto main """

        event_type = "keyboard_event"

        if key == keyboard.Key.esc:
            client_time = get_client_time()
            self.os_input_events.append([client_time, event_type, key])
            return False

def get_client_time():
    return datetime.now(timezone.utc).isoformat()

def send_log(event_name ,coordinates):

    payload = {
        "client_time": datetime.now(timezone.utc).isoformat(),
        "source": "client",
        "event": event_name,
        "data": {'coordinates': coordinates}
    }
    
    data = json.dumps(payload).encode("UTF-8")

    try:

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(data, (SERVER_HOST, SERVER_PORT))

    except Exception as e:
        print(f"Failed to send UDP packet: {e}")


def main(): 
    
    recorder = InputRecording()

    mouse_listener = mouse.Listener(on_click=recorder.on_click)
    keyboard_listener = keyboard.Listener(on_press=recorder.on_press, on_release=recorder.on_release)

    mouse_listener.start()
    keyboard_listener.start()

    print("checkpoint1: listener started")

    try: 
        while keyboard_listener.running and mouse_listener.running: 
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stop it.")

    finally:
        mouse_listener.stop()
        keyboard_listener.stop()

        keyboard_listener.join()
        mouse_listener.join()

    print("checkpoint2: print the values")

    # temporary just to get it working and then will integrate it live 
    for event in recorder.os_input_events:
        print(event)

    print("checkpoint3: script end")


if __name__ == "__main__":
    main() 