NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def midi_note_to_name(note_num):
    octave = (note_num // 12) - 1  # Octave starts at 0 for C-1, but we want it to start at 1 for C0
    note = NOTE_NAMES[note_num % 12]  # Get the note name based on the note number (0-11)
    return f"{note}{octave}"