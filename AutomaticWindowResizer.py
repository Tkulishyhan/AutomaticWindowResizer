# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import configparser
import pygetwindow as gw
from pynput import keyboard
import pyautogui

# Initialize the Tkinter main window
root = tk.Tk()
root.title("Window Arranger v0.1 by S.A. Li")
root.geometry("400x300")  # Set the startup size of the GUI window to 400x300

# Now it's safe to create Tkinter variables
window_info_var = tk.StringVar(value="No window selected")
instruction_var = tk.StringVar(value="Click 'Select Window' then press F3 to choose a window.")
f3_listen_flag = False

# Key press listening callback function
def on_press(key):
    global selected_window_info, f3_listen_flag
    if f3_listen_flag and key == keyboard.Key.f3:  # Check the F3 key
        x, y = pyautogui.position()  # Get the current mouse position
        selected_windows = gw.getWindowsAt(x, y)
        if selected_windows:
            selected_window = selected_windows[0]
            selected_window_info = {
                'title': selected_window.title,
                'width': selected_window.width,
                'height': selected_window.height,
                'x': selected_window.left,
                'y': selected_window.top
            }
            # Update the information of the selected window on the GUI
            window_info_var.set(f"Title: {selected_window_info['title']}, Size: {selected_window_info['width']}x{selected_window_info['height']}, Position: ({selected_window_info['x']},{selected_window_info['y']})")
            # Stop listening to the F3 key and immediately save the window information
            f3_listen_flag = False
            save_window_info()  # Call the save window information function immediately

# Function to start listening to the F3 key
def start_listen_f3():
    global f3_listen_flag
    f3_listen_flag = True
    #instruction_var.set("Press F3 Key to select window.")
    message_text.delete('1.0', tk.END)  # Clear previous content
    message_text.insert(tk.END, f"Press F3 Key to select window.")

# Start listening for key events
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Function to save window information
def save_window_info():
    global selected_window_info
    if selected_window_info:
        # Get the configuration file
        config = configparser.ConfigParser()
        config.read('mw.ini', encoding='utf-8')

        # Create a unique section name for the new window
        new_section_index = 1 + len(config.sections())  # Create a new index by adding the existing number of sections
        section_name = f"Window{new_section_index}"  # Create a section name based on the new index

        # Add or update window information
        if not config.has_section(section_name):
            config.add_section(section_name)
        config.set(section_name, 'title', selected_window_info['title'])
        config.set(section_name, 'width', str(selected_window_info['width']))
        config.set(section_name, 'height', str(selected_window_info['height']))
        config.set(section_name, 'x', str(selected_window_info['x']))
        config.set(section_name, 'y', str(selected_window_info['y']))

        # Write back to the configuration file
        with open('mw.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        # Update the Text widget to display the success message
        message_text.delete('1.0', tk.END)  # Clear previous content
        message_text.insert(tk.END, f"Window parameters for '{selected_window_info['title']}' have been saved under section [{section_name}] in mw.ini file.")

        window_info_var.set("No window selected")  # Clear the displayed window information
        selected_window_info = None  # Clear the saved window information

# Function to arrange windows based on saved settings
def arrange_windows():
    config = configparser.ConfigParser()
    config.read('mw.ini', encoding='utf-8')

    for section in config.sections():
        if config.has_option(section, 'title'):
            window_title = config.get(section, 'title')
            new_width = config.getint(section, 'width')
            new_height = config.getint(section, 'height')
            x = config.getint(section, 'x')
            y = config.getint(section, 'y')

            windows_with_title = gw.getWindowsWithTitle(window_title)
            for win in windows_with_title:
                if win.title == window_title:  # Ensure it's the correct window
                    win.size = (new_width, new_height)
                    win.moveTo(x, y)
                    break  # Stop searching after finding the matching window

# GUI setup
instruction_label = tk.Label(root, textvariable=instruction_var)
instruction_label.pack(pady=5)

select_window_button = tk.Button(root, text="Select Window", command=start_listen_f3)
select_window_button.pack(pady=5)

info_label = tk.Label(root, textvariable=window_info_var, wraplength=380)
info_label.pack(pady=10)

arrange_button = tk.Button(root, text="Arrange Windows", command=arrange_windows)
arrange_button.pack(pady=10)

# Create a frame for the message Text widget and its Scrollbar
message_frame = tk.Frame(root)
message_frame.pack(fill=tk.BOTH, expand=True)
message_text = tk.Text(message_frame, height=4, width=50)
scroll = tk.Scrollbar(message_frame, command=message_text.yview)
message_text.configure(yscrollcommand=scroll.set)
message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

root.mainloop()

# Stop listening
listener.stop()
