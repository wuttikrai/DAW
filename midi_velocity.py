from midiutil import MIDIFile

# Setup the MIDI file (1 track)
midi_file = MIDIFile(1)
track = 0
time_start = 0 
bpm = 120

# Add track name and tempo
midi_file.addTrackName(track, time_start, "One Hit Per Bar Sweep")
midi_file.addTempo(track, time_start, bpm)

# MIDI Channel 10 (index 9) for drums
channel = 9 
pitch_instrument = 42  # 42 = Closed Hi-Hat (or try 36 for a heavy Kick Drum)
duration = 1.0         # Quarter note duration

# This automatically generates the exact list you provided: [1, 2, 3 ... 127]
velocities = list(range(1, 128))

# Generate one note per bar for all 127 velocities
for bar, velocity in enumerate(velocities):
    # Calculate the starting time for each bar (assuming 4 beats per bar)
    # Bar 0 starts at time 0, Bar 1 starts at time 4, Bar 2 starts at time 8, etc.
    note_time = bar * 4 
    
    # Add the note on Beat 1 of the current bar
    midi_file.addNote(track, channel, pitch_instrument, note_time, duration, velocity)

# Write the data to a new .mid file
with open("drum_loop_bar_sweep.mid", "wb") as output_file:
    midi_file.writeFile(output_file)

print("Successfully generated drum_loop_bar_sweep.mid! (Length: 127 bars)")
