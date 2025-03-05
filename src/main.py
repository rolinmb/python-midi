import ctypes
from ctypes import wintypes
import sys

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
    print(f"Callback triggered; message: {wMsg}")
    if wMsg == 0x3C3:  # MIM_DATA (MIDI message received)
        status = dwParam1 & 0xFF
        data1 = (dwParam1 >> 8) & 0xFF
        data2 = (dwParam1 >> 16) & 0xFF
        print(f"Received MIDI: Status={hex(status)}, Data1={data1}, Data2={data2}")
        sys.stdout.flush()

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
