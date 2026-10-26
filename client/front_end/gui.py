import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import threading
import requests
from datetime import datetime, timezone
from pynput import keyboard
import socket

import dearpygui.dearpygui as dpg

from listeners import os_input_listener, target_listener

API = "http://127.0.0.1:8000"
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000
SOCKET_TIMEOUT = 0.5 # Time for the client to listen to the target's sock

class State:
    session_id = None
    is_recording = False
    is_paused = False

    stop_event = threading.Event()
    target_sock: socket.socket | None = None
    target_thread: threading.Thread | None = None
    
    recorder: os_input_listener.InputRecording | None = None
    stop_key = "esc"
    listening_for_key = False


def log(message):
    time = datetime.now(timezone.utc).strftime("%H:%M:%S")
    log_line = f"[{time}] {message}"
    print(log_line)
    if dpg.does_item_exist("log_box"):
        current = dpg.get_value("log_box")
        log_lines = current.strip().split("\n") if current.strip() else []
        log_lines.append(log_line)
        dpg.set_value("log_box", "\n".join(log_lines[-100:]))


def api_create_session(subject_id):
    request = requests.post(f"{API}/sessions", json={"subject_id": subject_id}, timeout=5)
    request.raise_for_status()
    return request.json()["session_id"]


def api_start_session(session_id):
    request = requests.put(f"{API}/sessions/start/{session_id}", timeout=5)
    request.raise_for_status()


def api_end_session(session_id):
    request = requests.put(f"{API}/sessions/end/{session_id}", timeout=5)
    request.raise_for_status()


def api_enter_log(session_id, payload):
    # Ensure client_time exists
    if "client_time" not in payload or not payload["client_time"]:
        payload["client_time"] = datetime.now(timezone.utc).isoformat()
    # Ensure required fallback values if fields are missing or None
    if "target_time" not in payload or not payload["target_time"]:
        payload["target_time"] = payload["client_time"]
    payload["source"] = payload.get("source") or "client"
    payload["target"] = payload.get("target") or "Unknown Target"
    payload["event"] = payload.get("event") or "Unknown Event"
    if "data" not in payload or payload["data"] is None:
        payload["data"] = {}

    request = requests.post(f"{API}/logs/{session_id}", json=payload, timeout=5)
    request.raise_for_status()


def forward_event(payload, label):

    if State.session_id:
        try:
            api_enter_log(State.session_id, payload)
            
            log(f"[{label}] Forwarded to server: {payload.get('event','?')}, data:{payload.get('data','?')}")
        
        except requests.HTTPError as e:
            log(f"[{label}] Failed: {e}")

            if e.response is not None:
                log(f"[API] Validation details: {e.response.text}")

        except Exception as e:
            log(f"[{label}] Failed: {e}")
      
            
def on_os_event(event):
    # Disable OS logs temporarily
    return 
    if not State.is_recording:
        return

    threading.Thread(target=forward_event, args=(event, "OS"), daemon=True).start()


def start_target_thread():

    # If the listener is running, skip the rest of the function to prevent multiple threads on one service
    if State.target_thread and State.target_thread.is_alive():
        return False

    State.target_thread = threading.Thread(
        target=target_loop,
        name="TargetListener",
        daemon=True
    )
    
    State.target_thread.start()
    return True


def target_loop():
    sock = None

    try:
        sock = target_listener.target_connect(TARGET_HOST, TARGET_PORT)
        sock.settimeout(SOCKET_TIMEOUT)
        State.target_sock = sock

        log(f"[TARGET] Listening on {TARGET_HOST}:{TARGET_PORT}")

        while not State.stop_event.is_set():
            try: 
                payload, __ = target_listener.listen(sock)
            except socket.timeout:
                continue

            if State.stop_event.is_set():
                break
            
            if payload is None:
                continue

            if State.is_recording:
                forward_event(payload, "TARGET")
        
    except OSError as e:
        if not State.stop_event.is_set():
            log(f"[TARGET] Bind failed: {e}")

    finally:
        if sock:
            sock.close()

        if State.target_sock is sock:
            State.target_sock = None
        

def on_start():

    # stop_key = State.stop_key

    subject = dpg.get_value("subject_input").strip()
    if not subject:
        log("[UI] Enter a Subject ID first")
        return

    try:
        session_id = api_create_session(subject)
        log(f"[SESSION] Created Session: {session_id}")

        api_start_session(session_id)
        State.session_id = session_id
        log(f"[SESSION] Started Session: {session_id}")
    
    except Exception as e:
        log(f"[SESSION] Failed: {e}")
        State.session_id = None
        return

    State.stop_event.clear()
    State.is_recording = True
    State.is_paused = False

    try:
        State.recorder = os_input_listener.InputRecording(on_event = on_os_event, stop_key = State.stop_key, on_stop = on_stop)    
        State.recorder.start()
        start_target_thread()
    
    except Exception as e:
        log(f"[SESSION] Startup failed: {e}")
        on_stop()
        return

    update_ui()


def on_pause():

    if not State.is_recording:
        return 

    State.stop_event.set()
    State.is_recording = False
    State.is_paused = True

    if State.recorder:
        State.recorder.disable()

    if State.target_thread:
        State.target_thread.join(timeout=1)

    log(f"[SESSION] Paused Session: {State.session_id}")

    update_ui()


def on_resume():

    if not State.is_paused:
        return 

    if State.target_thread and State.target_thread.is_alive():
        State.target_thread.join(timeout=1)

        if State.target_thread.is_alive():
            return
    
    State.stop_event.clear()

    if not start_target_thread():
        State.stop_event.set()
        return 

    if State.recorder: 
        State.recorder.enable()

    State.is_recording = True
    State.is_paused = False

    log(f"[SESSION] Resumed Session: {State.session_id}")
    
    update_ui()


def on_stop():

    State.stop_event.set()
    State.is_recording = False
    State.is_paused = False

    if State.recorder:
        State.recorder.stop()
        State.recorder = None

    if State.target_thread:
        State.target_thread.join(timeout=1)

    if State.session_id:
        try:
            api_end_session(State.session_id)
            log(f"[SESSION] Ended Session: {State.session_id}")
        
        except Exception as e:
            log(f"[SESSION] End failed: {e}")

        finally:
            State.session_id = None

    update_ui()


def on_set_stop_key():

    def capture(key):

        try:
            key_name = key.char

        except AttributeError:
            key_name = str(key).split(".")[-1]

        State.stop_key = key_name
        State.listening_for_key = False
        dpg.configure_item("btn_set_stop_key", label=key_name, enabled=True)

        return False 

    State.listening_for_key = True
    dpg.configure_item("btn_set_stop_key", label="[ press a key ]", enabled=False)

    keyboard.Listener(on_press=capture).start()


def update_ui():
    has = State.session_id is not None
    is_recording = State.is_recording
    is_paused = State.is_paused

    dpg.configure_item("subject_input", enabled=not has)
    dpg.configure_item("btn_start", enabled=not has)
    dpg.configure_item("btn_pause", enabled=is_recording)
    dpg.configure_item("btn_resume", enabled=is_paused)
    dpg.configure_item("btn_stop", enabled=has)
    dpg.configure_item("btn_set_stop_key", enabled=not has)

    if is_recording:
        dpg.set_value("status_text", "[STATUS] RECORDING")
        dpg.configure_item("status_text", color=(80, 220, 120, 255))
    elif is_paused:
        dpg.set_value("status_text", "[STATUS] PAUSED")
        dpg.configure_item("status_text", color=(220, 180, 60, 255))
    else:
        dpg.set_value("status_text", "[STATUS] IDLE")
        dpg.configure_item("status_text", color=(160, 160, 170, 255))


def main():

    colour_white = (255, 255, 255, 255)
    colour_black = (33, 28, 33, 255)
    colour_black_lighter = (66, 56, 66, 255)
    colour_blue = (61, 85, 123, 255)
    colour_blue_darker = (47, 66, 96, 255)

    dpg.create_context()

    theme = dpg.add_theme()
    group_component_01 = dpg.add_theme_component(dpg.mvAll, parent=theme) 
    dpg.add_theme_color(dpg.mvThemeCol_WindowBg, colour_black, parent=group_component_01)
    dpg.add_theme_color(dpg.mvThemeCol_FrameBg, colour_black_lighter,  parent=group_component_01)
    dpg.add_theme_color(dpg.mvThemeCol_Button, colour_blue, parent=group_component_01)
    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, colour_blue_darker, parent=group_component_01)
    dpg.add_theme_color(dpg.mvThemeCol_Text, colour_white, parent=group_component_01)
    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4, parent=group_component_01)
    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 8, parent=group_component_01)
    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6, parent=group_component_01)
    dpg.bind_theme(theme)

    dpg.create_viewport(title="SRL LOGGER", width=520, height=460, resizable=False)
    dpg.setup_dearpygui()
    window = dpg.add_window(tag="win", no_title_bar=True, no_move=True, no_resize=True, no_scrollbar=True)
    dpg.push_container_stack(window)
    
    dpg.add_spacer(height=8)

    dpg.add_text("CURRENT STATUS OF LOGGER")
    dpg.add_text("[STATUS] IDLE", tag="status_text", color=colour_white)

    dpg.add_separator()
    dpg.add_spacer(height=6)

    dpg.add_text("SUBJECT ID")
    dpg.add_input_text(tag="subject_input", hint="i.e. subject01", width=-1)
    dpg.add_spacer(height=6)

    group_component_02 = dpg.add_group(horizontal=True)
    dpg.add_button(label="Start", tag="btn_start", width=150, height=36, callback=on_start, parent=group_component_02)
    dpg.add_button(label="Pause", tag="btn_pause", width=150, height=36, callback=on_pause, enabled=False, parent=group_component_02)
    dpg.add_button(label="Resume", tag="btn_resume", width=150, height=36, callback=on_resume, enabled=False, parent=group_component_02)
    dpg.add_button(label="Stop", tag="btn_stop", width=150, height=36, callback=on_stop, enabled=False, parent=group_component_02)
    dpg.add_spacer(height=6)
    dpg.bind_item_theme(group_component_02, theme)

    dpg.add_text("STOP RECORDING KEYBIND")

    group_component_03 = dpg.add_group(horizontal=True)
    dpg.add_button(label=State.stop_key, tag="btn_set_stop_key", width=150, height=36, callback=on_set_stop_key, parent=group_component_03)        

    dpg.add_spacer(height=6)
    dpg.add_separator()
    dpg.add_spacer(height=6)

    dpg.add_text("AUDIT LOG")
    dpg.add_input_text(tag="log_box", multiline=True, readonly=True, width=-1, height=-1)
    dpg.pop_container_stack()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        dpg.set_item_width("win", dpg.get_viewport_client_width())
        dpg.set_item_height("win", dpg.get_viewport_client_height())
        dpg.set_item_pos("win", [0, 0])
        dpg.render_dearpygui_frame()

    on_stop()
    dpg.destroy_context()


if __name__ == "__main__":
    main()

