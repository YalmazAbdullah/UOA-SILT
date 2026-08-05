from datetime import datetime,timezone

import dearpygui.dearpygui as dpg

dummy_log = {
    "log_id":"2434",
    "target_time":datetime.now(timezone.utc).isoformat(),
    "client_time":datetime.now(timezone.utc).isoformat(),
    "server_time":datetime.now(timezone.utc).isoformat(),
    "source":"client",
    "target":None,
    "event":"Test",
    "data":{}
}

dummy_session = {
    "session_id": "14114514",
    "subject_id": "mito",
    "session_state": "started",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "started_at": None,
    "ended_at": None
}

TITLE = "SILT-Monitor"

def drag_viewport(sender, app_data):
    '''
    Handles the logic of dragging around an undecorated viewport. This is needed because docking branch of
    imgui is not integrated into dpg\\
    Credit: @v-ein\\
    Link: https://github.com/my1e5/dpg-examples/blob/main/window/drag_undecorated_viewport.py 
    '''
    FRAME_PADDING_Y = 3
    _, drag_dx, drag_dy = app_data
    drag_start_y = dpg.get_mouse_pos(local=False)[1] - drag_dy
    title_bar_height = 2*FRAME_PADDING_Y + dpg.get_text_size("")[1]
    if drag_start_y < title_bar_height:  # only drag the viewport when dragging the title bar
        x_pos, y_pos = dpg.get_viewport_pos()
        dpg.set_viewport_pos((x_pos + drag_dx, max(0, y_pos + drag_dy)))

def prepare_session_table():
    session_table = dpg.add_table(
        scrollY=True,
        row_background=True,
        resizable=True,
        borders_innerH=True, borders_innerV=True)
    dpg.add_table_column(label="Sessions ID", parent = session_table)
    dpg.add_table_column(label="Subject", parent = session_table)
    dpg.add_table_column(parent = session_table)
    return session_table

g_ACTIVE_SESSION = None
def inspect_session_cb(sender, app_data, user_data):
    global g_ACTIVE_SESSION
    if(g_ACTIVE_SESSION == None):
        dpg.hide_item("no_session_view")
        dpg.show_item("session_view")
    g_ACTIVE_SESSION = user_data
    # unsubscribe websocket
    # subsribe to websocket
    # delete all table rows
    #   pg.delete_item("log_table_parent", children_only=True)

def add_session_row(session_data, table):
    with dpg.table_row(parent=table):
        dpg.add_text(session_data["session_id"])
        dpg.add_text(session_data["subject_id"])
        dpg.add_button(label="inspect", 
                       callback=inspect_session_cb, 
                       user_data=session_data["session_id"])

def prepare_log_table(parent):
    log_table = dpg.add_table(
        scrollY=True,
        row_background=True,
        resizable=True,
        borders_innerH=True, borders_innerV=True, 
        parent=parent)
    dpg.add_table_column(label = "ID", parent=log_table)
    dpg.add_table_column(label = "Name", parent=log_table)
    dpg.add_table_column(label = "Source", parent=log_table)
    dpg.add_table_column(label = "Target", parent=log_table)
    dpg.add_table_column(label = "server_time", parent=log_table)
    dpg.add_table_column(label = "client_time", parent=log_table)
    dpg.add_table_column(label = "target_time", parent=log_table)
    return log_table

def add_log_row(log_data, log_tables):
    table = "event_table"
    if(log_data["event"].startswith("Mouse")):
        table = "mouse_table"
    elif(log_data["event"].startswith("Mouse")):
        table = "keyboard_table"
    with dpg.table_row(parent=log_tables[table]):
        dpg.add_text(log_data["log_id"])
        dpg.add_text(log_data["event"])
        dpg.add_text(log_data["source"])
        dpg.add_text(log_data["target"])
        dpg.add_text(log_data["server_time"])
        dpg.add_text(log_data["client_time"])
        dpg.add_text(log_data["target_time"])

dpg.create_context()
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize,1,1,category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,2,2,category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing,2,4,category=dpg.mvThemeCat_Core)
dpg.bind_theme(global_theme)
with dpg.handler_registry():
    dpg.add_mouse_drag_handler(button=0, threshold=0.0, callback=drag_viewport)
with dpg.window(label=TITLE, on_close=lambda: dpg.stop_dearpygui()) as primary_window:
    # GUI Body
    root = dpg.add_group(horizontal=True)
    with dpg.child_window(width = 300,  resizable_x=True, border=False, parent=root) as left_pane:
        session_table = prepare_session_table()
        for i in range(5):
            add_session_row(dummy_session, session_table)
    with dpg.child_window(width = -1, parent=root) as right_pane:
        log_tables = {}
        with dpg.tab_bar(tag='session_view'):
            event_tab = dpg.add_tab(label="Event")
            log_tables["event_table"] = prepare_log_table(event_tab)
            mouse_tab = dpg.add_tab(label="Mouse")
            log_tables["mouse_table"] = prepare_log_table(mouse_tab)
            keyboard_tab = dpg.add_tab(label="Keyboard")
            log_tables["keyboard_table"] = prepare_log_table(keyboard_tab)
        dpg.hide_item ("session_view")
        dpg.add_text(" No session selected...", tag="no_session_view")

dpg.create_viewport(title=TITLE)
dpg.set_primary_window(primary_window, True)
dpg.configure_item(primary_window, no_title_bar=False)
dpg.set_viewport_decorated(False)
dpg.setup_dearpygui()
dpg.show_style_editor()
# dpg.show_metrics()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()