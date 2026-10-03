# Credit @v-ein - see https://discord.com/channels/736279277242417272/1191409079025930340/1191409079025930340
# see also drag_menu_bar.py
import dearpygui.dearpygui as dpg
from PIL import Image
import numpy as np

dpg.create_context()




def drag_viewport(sender, app_data):
    FRAME_PADDING_Y = 3
    _, drag_dx, drag_dy = app_data

    # Note: at this point, the mouse has already moved off the starting point,
    # but to do a hit-test on the title bar, we need the starting point so we go
    # back to it.
    drag_start_y = dpg.get_mouse_pos(local=False)[1] - drag_dy
    title_bar_height = 2*FRAME_PADDING_Y + dpg.get_text_size("")[1]
    if drag_start_y < title_bar_height:  # only drag the viewport when dragging the title bar
        x_pos, y_pos = dpg.get_viewport_pos()

        # We're limiting the y position so that the viewport doesn't go off the top of the screen
        dpg.set_viewport_pos((x_pos + drag_dx, max(0, y_pos + drag_dy)))







def pil_to_dpg_texture(pil_image):
    """Converts a Pillow Image into a normalized 1D float list for Dear PyGui."""
    # 1. Force image into RGBA mode (adds alpha channel if missing)
    rgba_image = pil_image.convert("RGBA")
    
    # 2. Convert to a fast NumPy array
    img_array = np.array(rgba_image, dtype=np.float32)
    
    # 3. Normalize pixel values from 0-255 down to 0.0-1.0
    img_array /= 255.0
    
    # 4. Flatten the 3D array into a 1D list
    texture_data = img_array.flatten().tolist()
    
    return texture_data


with dpg.handler_registry():
    dpg.add_mouse_drag_handler(button=0, threshold=0.0, callback=drag_viewport)

window_title = "Test title bar"
image = Image.open('test_ss.png')
width, height = image.size
target_width = 500
target_height = int(height * (target_width / width))
resized_image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
texture_data = pil_to_dpg_texture(resized_image)
with dpg.texture_registry():
    dpg.add_dynamic_texture(width=target_width, height=target_height, default_value=texture_data, tag="texture_tag")

with dpg.window(label=window_title, on_close=lambda: dpg.stop_dearpygui()) as wnd:
    with dpg.group(horizontal=True):
        with dpg.child_window(width = 300,  resizable_x=True):
            with dpg.table(resizable=True,borders_innerH=True, borders_innerV=True):
                # use add_table_column to add columns to the table,
                # table columns use child slot 0
                dpg.add_table_column(label = "session_id")
                dpg.add_table_column(label = "session_name")
                dpg.add_table_column(label = "session_status")

                for i in range(0, 4):
                    with dpg.table_row():
                        for j in range(0, 3):
                            dpg.add_text(f"Row{i} Column{j}")
        with dpg.child_window(width = -1, border=False):
            with dpg.table():
                dpg.add_table_column(width_stretch=True)
                dpg.add_table_column(width_fixed=True)
                dpg.add_table_column(width_stretch=True)
                with dpg.table_row():
                    dpg.add_text()
                    dpg.add_image("texture_tag")
                    dpg.add_text()

            with dpg.tab_bar(tag='tab_bar'):
                with dpg.tab(label="Event", tag='Event'):
                    with dpg.table(resizable=True,borders_innerH=True, borders_innerV=True):
                                    # use add_table_column to add columns to the table,
                                    # table columns use child slot 0
                                    dpg.add_table_column(label = "session_id")
                                    dpg.add_table_column(label = "session_name")
                                    dpg.add_table_column(label = "session_status")
                    
                                    for i in range(0, 4):
                                        with dpg.table_row():
                                            for j in range(0, 3):
                                                dpg.add_text(f"Row{i} Column{j}")
                with dpg.tab(label="Mouse", tag='Mouse'):
                    pass
                with dpg.tab(label="Keyboard", tag='Keyboard'):
                                    pass



dpg.create_viewport(title=window_title)
dpg.set_primary_window(wnd, True)
dpg.configure_item(wnd, no_title_bar=False)
dpg.set_viewport_decorated(False)

dpg.setup_dearpygui()
dpg.show_metrics()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()