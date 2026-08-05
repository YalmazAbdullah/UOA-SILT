import socket
import json
import time
import threading 
from datetime import datetime, timezone 
from pynput import mouse, keyboard

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000 

class InputRecording:
    def __init__(self, on_event = None) -> None:
        self._on_event = on_event
        self._enabled = threading.Event()
        self._enabled.set()

        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

    def enable(self):
        self._enabled.set()

    def disable(self):
        self._enabled.clear()

    def is_enabled(self):
        return self._enabled.is_set()

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

        self.mouse_listener.join()
        self.keyboard_listener.join()
    
    def send_event(self, event):
        if not self._enabled.is_set():
            return

        if self._on_event is not None:
            try: 
                self._on_event(event)
            except Exception as error:
                print(f"{error}")

    def on_click(self, x, y , mouse_button, is_pressed):

        if not is_pressed:
            return 

        self.send_event({
            "client_time": get_client_time(),
            "source": "client",
            "event": f"mouse_click",
            "data": {
                "x-pos:": x,
                "y-pos:": y,
                "mouse_button": mouse_button.name,
            }
        })

    def on_press(self, key):

        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key).split(".")[-1]

        self.send_event({
            "client_time": get_client_time(),
            "source": "client",
            "event": f"keyboard_press_{key_name}",
            "data": {
                "key": key_name
            }
        })

    def on_release(self, key):
        if not self._enabled.is_set():
            return

        try: 
            key_name = key.char
        except AttributeError:
            key_name = str(key).split(".")[-1]

        self.send_event({
            "client_time": get_client_time(),
            "source": "client",
            "event": f"keyboard_release_{key_name}",
            "data": {
                "key": key_name
            }
        })

def get_client_time():
    return datetime.now(timezone.utc).isoformat()

def repackage_payload(payload):

    return {
        "client_time": get_client_time(),
        "source": "client",
        "event": payload.get("event"),
        "data": payload.get("data")
    }

def main(): 

    def on_event(event):
        print(f"Event received: {event}")

    recorder = InputRecording(on_event=on_event)
    recorder.start()
    print("Started.")

    try:
        while recorder.keyboard_listener.running and recorder.mouse_listener.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stop it.")
    finally:
        recorder.stop()

    print("End.") 


if __name__ == "__main__":
    main() 