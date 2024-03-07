# -*- coding: utf-8 -*-  # Specify the encoding used (UTF-8)
import tkinter as tk  # Import the Tkinter library for GUI development
from tkinter import messagebox  # Import the messagebox class from Tkinter for pop-up messages
import configparser  # Import the configparser library for handling settings files
import pygetwindow as gw  # Import the PyGetWindow library for window management
from pynput import keyboard  # Import the keyboard module from pynput for listening to keyboard events
import pyautogui  # Import the PyAutoGUI library for GUI automation tasks

# Initialize the Tkinter main window
root = tk.Tk()
root.title("Automatic Window Resizer 2024.3.7")  # Set the window title
root.geometry("400x300")  # Set the startup size of the GUI window

# Safe to create Tkinter variables for GUI feedback
window_info_var = tk.StringVar(value="No window selected. Press 'Select Window' and then F3.")  # Variable for window info display
f3_listen_flag = False  # Flag to control the F3 listening, used to activate or deactivate key listening

# Function called when a key press is detected
def on_press(key):
    global selected_window_info, f3_listen_flag  # Use global variables within function
    if f3_listen_flag and key == keyboard.Key.f3:  # Check if the F3 key was pressed
        x, y = pyautogui.position()  # Capture the current mouse position
        selected_windows = gw.getWindowsAt(x, y)  # Get the window at the mouse position
        if selected_windows:  # Check if any window was selected
            selected_window = selected_windows[0]  # Take the first window found under cursor
            selected_window_info = {  # Create a dictionary to hold the window's information
                'title': selected_window.title,  # Window's title
                'width': selected_window.width,  # Window's width
                'height': selected_window.height,  # Window's height
                'x': selected_window.left,  # Window's X position
                'y': selected_window.top  # Window's Y position
            }
            # Update GUI with the selected window info
            window_info_var.set(f"Selected: {selected_window_info['title']}")
            f3_listen_flag = False  # Reset flag to stop listening to F3 key
            save_window_info()  # Call function to save window configuration

# Function to enable F3 listening
def start_listen_f3():
    global f3_listen_flag  # Use the global variable within function
    f3_listen_flag = True  # Set the flag to True to start listening for F3 key
    message_text.insert(tk.END, "Press F3 Key to select a window.\n")  # Show instruction in GUI

# Start listening for F3 key events
listener = keyboard.Listener(on_press=on_press)  # Create a key listener
listener.start()  # Start the listener

# Function to save window configuration
def save_window_info():
    global selected_window_info  # Use the global variable within function
    if selected_window_info:  # Check if there is information to save
        config = configparser.ConfigParser()  # Create a configuration parser object
        config.read('mw.ini', encoding='utf-8')  # Read existing configuration from file
        section_name = f"Window-{len(config.sections()) + 1}"  # Generate a new section name
        if not config.has_section(section_name):  # Check if the section already exists
            config.add_section(section_name)  # If not, add a new section
        # Update configuration settings with the selected window's information
        for key, value in selected_window_info.items():
            config.set(section_name, key, str(value))  # Set each item in the section
        with open('mw.ini', 'w', encoding='utf-8') as configfile:  # Open the config file for writing
            config.write(configfile)  # Write the updated configuration back to file
        # Feedback to user via GUI
        message_text.insert(tk.END, f"Saved settings for '{selected_window_info['title']}' under [{section_name}].\n")

        window_info_var.set("Configuration saved. Select another window or rearrange.")  # Update GUI with feedback
        selected_window_info = None  # Clear the saved window information for next selection

# Function to rearrange windows based on saved settings
def arrange_windows():
    config = configparser.ConfigParser()  # Create a new configuration parser object
    config.read('mw.ini', encoding='utf-8')  # Read the configuration from file
    # Apply each saved window configuration
    for section in config.sections():  # Iterate through each section in the configuration
        if config.has_option(section, 'title'):  # Check if the section has a 'title' option
            apply_window_settings(config, section)  # Call function to apply settings for this window

# Applies window settings from the configuration
def apply_window_settings(config, section):
    window_title = config.get(section, 'title')  # Get the window title from configuration
    width = config.getint(section, 'width')  # Get the width
    height = config.getint(section, 'height')  # Get the height
    x = config.getint(section, 'x')  # Get the X position
    y = config.getint(section, 'y')  # Get the Y position
    windows_with_title = gw.getWindowsWithTitle(window_title)  # Get all windows with this title
    for win in windows_with_title:  # Iterate through found windows
        if win.title == window_title:  # Ensure it's the correct window
            win.resizeTo(width, height)  # Change the window's size
            win.moveTo(x, y)  # Move the window to the specified position
            break  # Stop after the first match to avoid affecting multiple windows with the same title

# GUI setup
instruction_label = tk.Label(root, textvariable=window_info_var)  # Label for instructions
instruction_label.pack(pady=5)

select_window_button = tk.Button(root, text="Select Window", command=start_listen_f3)  # Button to activate F3 listening
select_window_button.pack(pady=5)

arrange_button = tk.Button(root, text="Rearrange Windows", command=arrange_windows)  # Button to apply saved window arrangements
arrange_button.pack(pady=10)

# Text widget for messages and its Scrollbar
message_frame = tk.Frame(root)  # Frame to contain the message text widget and its scrollbar
message_frame.pack(fill=tk.BOTH, expand=True)
message_text = tk.Text(message_frame, height=5, width=50)  # Text widget for feedback messages
scroll = tk.Scrollbar(message_frame, command=message_text.yview)  # Scrollbar for the text widget
message_text.configure(yscrollcommand=scroll.set)  # Link scrollbar to text widget
message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

root.mainloop()  # Start the GUI event loop

# Stop listening when the GUI is closed
listener.stop()
