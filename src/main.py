import ctypes
from ctypes import wintypes
import sys
import tkinter as tk
from tkinter import scrolledtext
from util import midi_note_to_name

class MidiListener:
    def __init__(self, device_id=1):
        self.device_id = device_id
        self.winmm = ctypes.WinDLL('winmm')

        # Check for available MIDI devices
        num_devices = self.winmm.midiInGetNumDevs()
        if num_devices == 0:
            print("No MIDI input devices detected. Please check your MIDI device connection.")
            sys.exit(1)

        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title("MIDI Input Stream")
        self.root.geometry("400x300")

        # Scrolled Text widget for MIDI messages
        self.text_widget = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=15)
        self.text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Define the callback function type
        self.MidiInProc = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.UINT, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD)
        self.midi_callback_func = self.MidiInProc(self.midi_callback)

        # Open and start MIDI device
        self.hMidiIn = wintypes.HANDLE()
        self.winmm.midiInOpen(ctypes.byref(self.hMidiIn), self.device_id, self.midi_callback_func, 0, 0x30000)  # CALLBACK_FUNCTION flag
        self.winmm.midiInStart(self.hMidiIn)

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def midi_callback(self, hMidiIn, wMsg, dwInstance, dwParam1, dwParam2):
        """Handles incoming MIDI messages."""
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
            self.text_widget.insert(tk.END, msg)
            self.text_widget.see(tk.END)  # Auto-scroll to the latest message

    def on_close(self):
        """Closes the MIDI device and exits the application."""
        self.winmm.midiInStop(self.hMidiIn)
        self.winmm.midiInClose(self.hMidiIn)
        self.root.destroy()

    def run(self):
        """Runs the Tkinter main event loop."""
        self.root.mainloop()

if __name__ == "__main__":
    midi_listener = MidiListener()
    midi_listener.run()
