#!/usr/bin/env python3
"""
Text to Morse Code MIDI Converter
Converts text messages into Morse code and exports as MIDI file for use in Ableton Live.
"""

import argparse
from midiutil import MIDIFile

# Morse code lookup table
MORSE_TABLE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',   'E': '.',
    'F': '..-.',  'G': '--.',   'H': '....',  'I': '..',    'J': '.---',
    'K': '-.-',   'L': '.-..',  'M': '--',    'N': '-.',    'O': '---',
    'P': '.--.',  'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',  'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    ' ': '/'  # Word separator
}

def text_to_morse(text):
    """Convert text to Morse code string."""
    morse_code = []
    text = text.upper()
    
    for char in text:
        if char in MORSE_TABLE:
            morse_code.append(MORSE_TABLE[char])
        elif char == ' ':
            morse_code.append('/')
        else:
            print(f"Warning: Character '{char}' not supported, skipping...")
    
    return ' '.join(morse_code)


def morse_to_midi(morse_code, output_file, dot_duration=0.1, note=60, velocity=100, tempo=120):
    """
    Convert Morse code to MIDI file.
    
    Args:
        morse_code: String of Morse code (dots, dashes, spaces, slashes)
        output_file: Path to output MIDI file
        dot_duration: Duration of a dot in seconds (default 0.1 = 100ms)
        note: MIDI note number (default 60 = Middle C)
        velocity: MIDI velocity/volume (0-127, default 100)
        tempo: BPM tempo (default 120)
    """
    # ITU Morse timing standards:
    # - Dot: 1 unit
    # - Dash: 3 units
    # - Gap between dots/dashes in character: 1 unit
    # - Gap between letters: 3 units
    # - Gap between words: 7 units
    
    midi_file = MIDIFile(1)  # 1 track
    track = 0
    channel = 0
    time = 0  # Start at beat 0
    
    midi_file.addTempo(track, time, tempo)
    
    # Convert Morse code to MIDI events
    elements = morse_code.split()
    
    for i, element in enumerate(elements):
        if element == '/':
            # Word gap (7 units, but we already have 3 from letter gap)
            time += dot_duration * 4  # Add 4 more units
            continue
        
        # Process each dot/dash in the element (letter)
        for j, symbol in enumerate(element):
            if symbol == '.':
                # Dot: 1 unit duration
                duration = dot_duration
            elif symbol == '-':
                # Dash: 3 units duration
                duration = dot_duration * 3
            else:
                continue
            
            # Add note to MIDI
            midi_file.addNote(track, channel, note, time, duration, velocity)
            time += duration
            
            # Gap between dots/dashes within a letter: 1 unit
            if j < len(element) - 1:
                time += dot_duration
        
        # Gap between letters: 3 units
        if i < len(elements) - 1 and elements[i + 1] != '/':
            time += dot_duration * 3
    
    # Write MIDI file
    with open(output_file, 'wb') as f:
        midi_file.writeFile(f)
    
    print(f"✅ MIDI file created: {output_file}")
    print(f"   Total duration: {time:.2f} seconds")
    print(f"   Note: MIDI note {note} ({get_note_name(note)})")
    print(f"   Tempo: {tempo} BPM")


def get_note_name(midi_note):
    """Convert MIDI note number to note name."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note_name = notes[midi_note % 12]
    return f"{note_name}{octave}"


def main():
    parser = argparse.ArgumentParser(
        description="Convert text to Morse code MIDI file for Ableton Live",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python text_to_morse_midi.py "HELLO WORLD" -o hello.mid
  
  # Faster Morse code (shorter dots)
  python text_to_morse_midi.py "TEST" -o test.mid --dot 0.05
  
  # Different MIDI note (A4 = 440Hz)
  python text_to_morse_midi.py "SOS" -o sos.mid --note 69
  
  # Custom tempo
  python text_to_morse_midi.py "HELLO" -o hello.mid --tempo 140

MIDI Note Numbers:
  60 = Middle C (C4)
  69 = A4 (440 Hz)
  72 = C5 (one octave above middle C)
  
For Ableton:
  1. Run this script to generate a .mid file
  2. Drag the .mid file into an Ableton MIDI track
  3. Add any synth/instrument (e.g., Operator with sine wave for ultrasonic)
  4. Set the synth to play at 19kHz for ultrasonic output
        """
    )
    
    parser.add_argument('text', help='Text message to convert to Morse code')
    parser.add_argument('-o', '--output', help='Output MIDI file path')
    parser.add_argument('--dot', type=float, default=0.1,
                       help='Dot duration in seconds (default: 0.1)')
    parser.add_argument('--note', type=int, default=60,
                       help='MIDI note number (default: 60 = Middle C)')
    parser.add_argument('--velocity', type=int, default=100,
                       help='MIDI velocity/volume 0-127 (default: 100)')
    parser.add_argument('--tempo', type=int, default=120,
                       help='Tempo in BPM (default: 120)')
    parser.add_argument('--preview', action='store_true',
                       help='Show Morse code preview without creating MIDI file')

    args = parser.parse_args()

    # Convert text to Morse
    morse_code = text_to_morse(args.text)

    print(f"📝 Input Text: {args.text}")
    print(f"🔤 Morse Code: {morse_code}")
    print()

    if args.preview:
        print("Preview mode - no MIDI file created.")
        return

    # Check if output file is specified
    if not args.output:
        print("❌ Error: Output file (-o/--output) is required when not in preview mode.")
        print("   Use --preview to see Morse code without creating a file.")
        return
    
    # Create MIDI file
    morse_to_midi(
        morse_code=morse_code,
        output_file=args.output,
        dot_duration=args.dot,
        note=args.note,
        velocity=args.velocity,
        tempo=args.tempo
    )


if __name__ == '__main__':
    main()
