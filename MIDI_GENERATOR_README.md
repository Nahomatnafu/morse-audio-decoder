# Text to Morse Code MIDI Generator

Convert text messages to Morse code and export as MIDI files for use in Ableton Live and other DAWs.

## 🎹 Quick Start

### Basic Usage

```bash
python text_to_morse_midi.py "HELLO WORLD" -o hello.mid
```

This creates a MIDI file with:
- Your message converted to Morse code
- MIDI notes at Middle C (note 60)
- 100ms dot duration
- 120 BPM tempo

### Preview Morse Code (No File Created)

```bash
python text_to_morse_midi.py "TEST MESSAGE" --preview
```

Output:
```
📝 Input Text: TEST MESSAGE
🔤 Morse Code: - . ... - / -- . ... ... .- --. .
```

## 📋 Usage Examples

### Fast Morse Code (Shorter Duration)

```bash
python text_to_morse_midi.py "SOS" -o sos.mid --dot 0.05
```

### Custom MIDI Note (A4 = 440 Hz)

```bash
python text_to_morse_midi.py "HELLO" -o hello.mid --note 69
```

### Different Tempo

```bash
python text_to_morse_midi.py "TEST" -o test.mid --tempo 140
```

### Complete Example with All Options

```bash
python text_to_morse_midi.py "HELLO CHATGPT" -o message.mid --dot 0.08 --note 72 --velocity 110 --tempo 130
```

## ⚙️ Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text` | (required) | Text message to convert |
| `-o, --output` | None | Output MIDI file path (required unless --preview) |
| `--dot` | 0.1 | Dot duration in seconds |
| `--note` | 60 | MIDI note number (60 = Middle C) |
| `--velocity` | 100 | MIDI velocity/volume (0-127) |
| `--tempo` | 120 | Tempo in BPM |
| `--preview` | False | Show Morse code without creating file |

### MIDI Note Reference

Common MIDI note numbers:
- **60** = Middle C (C4) - Default
- **69** = A4 (440 Hz)
- **72** = C5 (one octave above middle C)
- **84** = C6 (two octaves above middle C)

## 🎛️ Using in Ableton Live

### Step 1: Generate MIDI File

```bash
python text_to_morse_midi.py "YOUR MESSAGE" -o message.mid
```

### Step 2: Import into Ableton

1. Drag the `.mid` file into an empty MIDI track in Ableton
2. The MIDI notes will appear on the track

### Step 3: Add Instrument

For **ultrasonic Morse code** (19 kHz):

1. Add **Operator** or **Wavetable** to the MIDI track
2. Configure for sine wave output:
   - **Operator**: Set Oscillator A to sine wave, set coarse tuning to get 19kHz
   - **Wavetable**: Use Basic → Sine, transpose up to ultrasonic range
3. Fine-tune the frequency to exactly 19000 Hz
4. Adjust the velocity if needed

For **audible Morse code**:
1. Add any synth or instrument
2. The MIDI notes will trigger at the pitch specified with `--note`

### Step 4: Export Audio

1. Set Ableton to export at 48kHz sample rate (to preserve ultrasonic)
2. Export as FLAC or WAV (lossless)
3. Do NOT export as low-bitrate MP3 (will remove ultrasonic content)

## 📝 Supported Characters

- **Letters**: A-Z (automatically converted to uppercase)
- **Numbers**: 0-9
- **Spaces**: Converted to word gaps in Morse code
- **Unsupported characters**: Will show a warning and be skipped

## ⏱️ Morse Code Timing (ITU Standard)

The script follows International Telecommunication Union (ITU) timing:

- **Dot**: 1 unit
- **Dash**: 3 units (3× dot length)
- **Gap between dots/dashes**: 1 unit
- **Gap between letters**: 3 units
- **Gap between words**: 7 units

Example with `--dot 0.1`:
- Dot = 0.1 seconds (100 ms)
- Dash = 0.3 seconds (300 ms)
- Letter gap = 0.3 seconds
- Word gap = 0.7 seconds

## 💡 Tips & Tricks

### For Ultrasonic Steganography

```bash
# Generate long message with shorter dots for faster transmission
python text_to_morse_midi.py "HELLO CHATGPT ARE YOU READY" -o message.mid --dot 0.08

# Then in Ableton:
# 1. Set synth to 19kHz sine wave
# 2. Mix with music on another track
# 3. Export as FLAC at 48kHz sample rate
```

### For Audible Morse Practice

```bash
# Slower Morse for learning
python text_to_morse_midi.py "HELLO WORLD" -o practice.mid --dot 0.2 --note 69

# Use A4 (440Hz) for clear audible tone
```

### Batch Processing

Create multiple files:
```bash
python text_to_morse_midi.py "HELLO" -o hello.mid
python text_to_morse_midi.py "TEST" -o test.mid
python text_to_morse_midi.py "SOS" -o sos.mid
```

## 🔍 Troubleshooting

### "Error: Output file (-o/--output) is required"

Solution: Add `-o filename.mid` or use `--preview` mode

### MIDI file won't import into Ableton

- Check file extension is `.mid` or `.midi`
- Try dragging directly into a MIDI track (not audio track)
- Ensure the file was created successfully (check for success message)

### Can't hear the Morse code in Ableton

- Make sure you've added an instrument to the MIDI track
- Check that the track is not muted
- For ultrasonic (19kHz), you won't hear it - use a spectrum analyzer to verify

### Morse code is too fast/slow

- Adjust the `--dot` parameter
- Smaller values = faster (e.g., `--dot 0.05`)
- Larger values = slower (e.g., `--dot 0.2`)

## 🎯 Workflow: Text → MIDI → Ultrasonic Audio

Complete workflow for creating ultrasonic Morse code:

```bash
# 1. Generate MIDI
python text_to_morse_midi.py "SECRET MESSAGE" -o secret.mid --dot 0.1

# 2. Open Ableton Live
# 3. Import secret.mid to MIDI track
# 4. Add Operator synth set to 19kHz sine wave
# 5. Add your music on another track
# 6. Export as FLAC (48kHz sample rate)
# 7. Decode with: python decode_morse.py output.flac --carrier 19000 --bw 1500 --dot 0.100
```

## 📦 Installation

This tool requires `midiutil`:

```bash
pip install midiutil
```

Or install all project dependencies:

```bash
pip install -r requirements.txt
```

## 🔗 Integration with Decoder

Files created with this tool are designed to work with the decoder:

1. **Generate MIDI**: `python text_to_morse_midi.py "HELLO" -o hello.mid --dot 0.1`
2. **Create audio in Ableton** at 19kHz
3. **Export as FLAC** at 48kHz
4. **Decode**: `python decode_morse.py output.flac --carrier 19000 --bw 1500 --dot 0.100`

The `--dot` parameter should match between generation and decoding for best results.

---

**Happy Morse coding! 📡🎵**
