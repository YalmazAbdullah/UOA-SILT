import sys
import os

from click import pause
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import threading
import requests
from datetime import datetime, timezone

import dearpygui.dearpygui as dpg

from listeners import os_input_listener, target_listener

API = "http://127.0.0.1:8000"
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000

class State:
    session_id = None
    is_recording = False
    is_paused = False
    stop_event = threading.Event()
    target_sock = None
    recorder = None   

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
    now = datetime.now(timezone.utc).isoformat()
    body = {
        "target_time": payload.get("target_time"),
        "client_time": payload.get("client_time", now),
        "source":      payload.get("source", "client"),
        "target":      payload.get("target", "NULL"),
        "event":       payload.get("event", "NULL"),
        "data":        payload.get("data", {}),
    }
    request = requests.post(f"{API}/logs/{session_id}", json=body, timeout=5)
    request.raise_for_status()

def forward_event(payload, label):

    log(f"[{label}] Event = {payload.get('event','?')}")

    if State.session_id:
        try:
            api_enter_log(State.session_id, payload)
            log(f"[{label}] Forwarded to server")
        except Exception as e:
            log(f"[{label}] Failed: {e}")

def on_os_event(event):

    if not State.is_recording:
        return
     
    threading.Thread(target=forward_event, args=(event, "OS"), daemon=True).start()

def target_loop():

    try:
        State.target_sock = target_listener.target_connect(TARGET_HOST, TARGET_PORT)
    except OSError as e:
        log(f"[TARGET] Bind failed: {e}")
        return

    while not State.stop_event.is_set():
        payload, __ = target_listener.listen(State.target_sock)

        if payload is None:
            continue

        forward_event(payload, "TARGET")

    if State.target_sock:
        State.target_sock.close()
        State.target_sock = None

def on_start():
    subject = dpg.get_value("subject_input").strip()
    if not subject:
        log("[GUI] Enter a Subject ID first.")
        return

    try:
        State.session_id = api_create_session(subject)
        log(f"[SESSION] Created id={State.session_id}")
        api_start_session(State.session_id)
        log(f"[SESSION] Started")
    except Exception as e:
        log(f"[SESSION] Failed: {e}")
        State.session_id = None
        return

    State.stop_event.clear()
    State.is_recording = True
    State.is_paused = False

    State.recorder = os_input_listener.InputRecording(on_event=on_os_event)
    State.recorder.start()
    log("[OS] Input listener started")

    threading.Thread(target=target_loop, daemon=True).start()

    update_ui()

def on_pause():
    State.is_recording = False
    State.is_paused = True

    if State.recorder:
        State.recorder.disable()

    State.stop_event.set()
    log("[SESSION] Paused")

    update_ui()

def on_resume():
    State.stop_event.clear()
    State.is_recording = True
    State.is_paused = False

    if State.recorder:
        State.recorder.enable()

    threading.Thread(target=target_loop, daemon=True).start()
    log("[SESSION] Resumed")

    update_ui()

def on_stop():
    State.stop_event.set()
    State.is_recording = False
    State.is_paused = False

    if State.recorder:
        State.recorder.stop()
        State.recorder = None
        log("[OS] Input listener stopped")

    if State.session_id:
        try:
            api_end_session(State.session_id)
            log(f"[SESSION] Ended id={State.session_id}")
        except Exception as e:
            log(f"[SESSION] End failed: {e}")
        State.session_id = None

    update_ui()

def update_ui():
    has = State.session_id is not None
    is_recording = State.is_recording
    is_paused = State.is_paused

    dpg.configure_item("subject_input", enabled=not has)
    dpg.configure_item("btn_start", enabled=not has)
    dpg.configure_item("btn_pause", enabled=is_recording)
    dpg.configure_item("btn_resume", enabled=is_paused)
    dpg.configure_item("btn_stop", enabled=has)

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
    dpg.create_context()

    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20, 20, 28, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (35, 35, 48, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (55, 75, 135, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (75, 100, 170, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (210, 215, 230, 255))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6)
    dpg.bind_theme(theme)

    dpg.create_viewport(title="SRL LOGGER", width=520, height=460, resizable=False)

    dpg.setup_dearpygui()

    window = dpg.add_window(tag="win", no_title_bar=True, no_move=True, no_resize=True, no_scrollbar=True)

    dpg.push_container_stack(window)

    dpg.add_spacer(height=8)
    dpg.add_text("CURRENT STATUS OF LOGGER", color=(140, 165, 255, 255))
    dpg.add_text("[STATUS] IDLE", tag="status_text", color=(160, 160, 170, 255))
    dpg.add_separator()
    dpg.add_spacer(height=6)

    dpg.add_text("SUBJECT ID")
    dpg.add_input_text(tag="subject_input", hint="i.e. subject01", width=-1)
    dpg.add_spacer(height=10)

    group = dpg.add_group(horizontal=True)
    dpg.add_button(label="Start", tag="btn_start", width=114, height=36, callback=on_start, parent=group)
    dpg.add_button(label="Pause", tag="btn_pause", width=114, height=36, callback=on_pause, enabled=False, parent=group)
    dpg.add_button(label="Resume", tag="btn_resume", width=114, height=36, callback=on_resume, enabled=False, parent=group)
    dpg.add_button(label="Stop", tag="btn_stop", width=114, height=36, callback=on_stop, enabled=False, parent=group)

    dpg.add_spacer(height=10)
    dpg.add_separator()
    dpg.add_spacer(height=4)
    dpg.add_text("AUDIT LOG", color=(140, 145, 180, 255))
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

