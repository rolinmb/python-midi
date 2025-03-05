import ctypes
from ctypes import wintypes
import sys
from util import midi_note_to_name

DEVICE_ID = 1

# Load winmm.dll (Windows multimedia API)
winmm = ctypes.WinDLL('winmm')

# Get number of MIDI input devices
num_devices = winmm.midiInGetNumDevs()
print(f"Number of MIDI input devices: {num_devices}")

if num_devices == 0:
    print("No MIDI input devices detected. Please check your MIDI device connection.")

# MIDI Callback Function (called when a MIDI message is received)
def midi_callback(hMidiIn, wMsg, dwInstance, dwParam1, dwParam2):
    #print(f"Callback triggered; message: {wMsg}")
    if wMsg == 0x3C3:  # MIM_DATA (MIDI message received)
        status = dwParam1 & 0xFF  # Extract the status byte
        data1 = (dwParam1 >> 8) & 0xFF  # Extract the first data byte (note number)
        data2 = (dwParam1 >> 16) & 0xFF  # Extract the second data byte (velocity)

        if status >= 0x90 and status <= 0x9F:  # Note-on message (0x90 to 0x9F)
            print(f"Note-on: Note={midi_note_to_name(data1)}, Velocity={data2}")
        elif status >= 0x80 and status <= 0x8F:  # Note-off message (0x80 to 0x8F)
            print(f"Note-off: Note={midi_note_to_name(data1)}, Velocity={data2}")
        else:
            print(f"Other MIDI message: Status={hex(status)}, Data1={data1}, Data2={data2}")
        sys.stdout.flush()  # Flush output immediately

# Define callback function type
MidiInProc = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.UINT, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD)

# Open MIDI Input Device
midi_callback_func = MidiInProc(midi_callback)
hMidiIn = wintypes.HANDLE()

winmm.midiInOpen(ctypes.byref(hMidiIn), DEVICE_ID, midi_callback_func, 0, 0x30000)  # CALLBACK_FUNCTION flag
winmm.midiInStart(hMidiIn)  # Start receiving MIDI messages

# Keep the program running to receive MIDI messages
try:
    print("Listening for MIDI input... Press Ctrl+C to exit.")
    while True:
        ctypes.windll.kernel32.Sleep(100)  # Prevent CPU overuse
except KeyboardInterrupt:
    print("\nClosing MIDI input.")
    winmm.midiInStop(hMidiIn)
    winmm.midiInClose(hMidiIn)
