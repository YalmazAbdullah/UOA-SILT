import dearpygui.dearpygui as dpg

dpg.create_context()

TOTAL_WIDTH = 500  # Total allocated width for both child windows

def on_child1_resize(sender, app_data):
    # Get the new width of the first child window
    current_width1 = dpg.get_item_width("child_1")
    
    # Calculate the remaining width for the second child window
    new_width2 = TOTAL_WIDTH - current_width1
    
    # Enforce a minimum width so it doesn't disappear completely
    if new_width2 < 50:
        new_width2 = 50
        # Prevent child_1 from growing past the limit
        dpg.set_item_width("child_1", TOTAL_WIDTH - 50)
    
    # Update the second child window's width
    dpg.set_item_width("child_2", new_width2)

with dpg.window(label="Main Split Window", width=600, height=400):
    # Arrange child windows side-by-side
    with dpg.group(horizontal=True):
        
        # Primary resizable child window
        with dpg.child_window(tag="child_1", width=250, height=300, resizable_x=True):
            dpg.add_text("Left Panel")
            dpg.add_text("Drag my RIGHT edge ->")
            
        # Secondary responsive child window (not resizable by user)
        with dpg.child_window(tag="child_2", width=250, height=300):
            dpg.add_text("Right Panel")
            dpg.add_text("I adjust automatically!")

# Create an item handler registry to catch the resize event
with dpg.item_handler_registry(tag="child_1_handlers"):
    dpg.add_item_resize_handler(callback=on_child1_resize)

# Bind the handler registry specifically to the first child window
dpg.bind_item_handler_registry("child_1", "child_1_handlers")

dpg.create_viewport(title="Responsive Child Windows", width=650, height=450)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()