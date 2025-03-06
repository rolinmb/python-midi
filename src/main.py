import ctypes
from ctypes import wintypes
import sys
import tkinter as tk
from tkinter import scrolledtext
from util import midi_note_to_name

DEVICE_ID = 1

# Load winmm.dll (Windows multimedia API)
winmm = ctypes.WinDLL('winmm')

# Get number of MIDI input devices
num_devices = winmm.midiInGetNumDevs()
if num_devices == 0:
    print("No MIDI input devices detected. Please check your MIDI device connection.")
    sys.exit(1)

# Create the Tkinter GUI
root = tk.Tk()
root.title("MIDI Input Stream")
root.geometry("400x300")

text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15)
text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# MIDI Callback Function
def midi_callback(hMidiIn, wMsg, dwInstance, dwParam1, dwParam2):
    if wMsg == 0x3C3:  # MIM_DATA (MIDI message received)
        status = dwParam1 & 0xFF  # Extract the status byte
        data1 = (dwParam1 >> 8) & 0xFF  # Extract the first data byte (note number)
        data2 = (dwParam1 >> 16) & 0xFF  # Extract the second data byte (velocity)

        if status >= 0x90 and status <= 0x9F:  # Note-on message
            msg = f"Note-on: {midi_note_to_name(data1)}, Velocity={data2}\n"
        elif status >= 0x80 and status <= 0x8F:  # Note-off message
            msg = f"Note-off: {midi_note_to_name(data1)}, Velocity={data2}\n"
        else:
            msg = f"Other MIDI: Status={hex(status)}, Data1={data1}, Data2={data2}\n"

        # Update the Text widget in the Tkinter event loop
        text_widget.insert(tk.END, msg)
        text_widget.see(tk.END)  # Auto-scroll to the latest message

# Define callback function type
MidiInProc = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.UINT, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD)

# Open MIDI Input Device
midi_callback_func = MidiInProc(midi_callback)
hMidiIn = wintypes.HANDLE()
winmm.midiInOpen(ctypes.byref(hMidiIn), DEVICE_ID, midi_callback_func, 0, 0x30000)  # CALLBACK_FUNCTION flag
winmm.midiInStart(hMidiIn)  # Start receiving MIDI messages

# Function to clean up MIDI input
def on_close():
    winmm.midiInStop(hMidiIn)
    winmm.midiInClose(hMidiIn)
    root.destroy()

# Bind the close event
root.protocol("WM_DELETE_WINDOW", on_close)

# Start the Tkinter main loop
root.mainloop()
