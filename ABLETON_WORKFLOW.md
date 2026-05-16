# Ableton Live Workflow for Ultrasonic Morse Code

Complete workflow for creating ultrasonic Morse code messages in Ableton Live using the MIDI generator.

## 🎯 Complete Workflow

### Step 1: Generate MIDI from Text

```bash
# Generate MIDI file from your message
python text_to_morse_midi.py "HELLO CHATGPT ARE YOU READY" -o my_message.mid --dot 0.1
```

Output:
```
📝 Input Text: HELLO CHATGPT ARE YOU READY
🔤 Morse Code: .... . .-.. .-.. --- / -.-. .... .- - --. .--. - / .- .-. . / -.-- --- ..- / .-. . .- -.. -.--

✅ MIDI file created: my_message.mid
   Total duration: 18.40 seconds
   Note: MIDI note 60 (C4)
   Tempo: 120 BPM
```

### Step 2: Import MIDI into Ableton Live

1. **Open Ableton Live**
2. **Create a new MIDI track** (Ctrl+Shift+T / Cmd+Shift+T)
3. **Drag `my_message.mid`** into the MIDI track
4. The Morse code pattern appears as MIDI notes!

### Step 3: Configure Ultrasonic Synth

#### Option A: Using Operator (Recommended)

1. **Add Operator** to the MIDI track
2. **Configure Oscillator A:**
   - Waveform: **Sine** (cleanest for ultrasonic)
   - Coarse: Adjust to reach ~19kHz
   - Fine: Fine-tune to exactly 19000 Hz
3. **Turn off all other oscillators** (B, C, D)
4. **Set Envelope:**
   - Attack: 0 ms (instant)
   - Decay: 0 ms
   - Sustain: 100%
   - Release: 5-10 ms (short)

#### Option B: Using Wavetable

1. **Add Wavetable** to the MIDI track
2. **Select Wavetable:**
   - Category: Basic Shapes
   - Wavetable: **Sine**
3. **Transpose:** Use the transpose control to reach ultrasonic range
4. **Filter:** Turn off or set to bypass

### Step 4: Verify Ultrasonic Frequency

Since 19kHz is inaudible, verify using a spectrum analyzer:

1. **Add Spectrum** to the track (from Audio Effects → Analysis)
2. **Play the MIDI clip**
3. **Check the spectrum analyzer** - you should see a peak at 19kHz

### Step 5: Mix with Music (Optional)

To hide the Morse code in music:

1. **Create a new audio track** for your music
2. **Import or create your music** on this track
3. **Balance levels:**
   - Music: Normal level (0 dB)
   - Morse code: Lower level (-6 to -12 dB)
4. **The ultrasonic signal is inaudible** but will be in the mix!

### Step 6: Export Audio

**Critical settings for preserving ultrasonic content:**

1. **File → Export Audio/Video**
2. **Format:**
   - ✅ **WAV** or **FLAC** (lossless)
   - ❌ **NOT MP3** (removes ultrasonic!)
3. **Sample Rate: 48000 Hz** (minimum for 19kHz carrier)
4. **Bit Depth: 24-bit** (recommended) or 16-bit
5. **Export!**

### Step 7: Verify with Decoder

Test your exported file:

```bash
python decode_morse.py my_output.flac --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.5 --min_bursts 10
```

Expected output:
```
[i] Loaded my_output.flac | Sample rate: 48000 Hz | Nyquist: 24000.0 Hz
Decoded:
  Morse : .... . .-.. .-.. --- / -.-. .... .- - --. .--. - / .- .-. . / -.-- --- ..- / .-. . .- -.. -.--
  Text  : HELLO CHATGPT ARE YOU READY
  Confidence: 0.98
```

## 🎨 Creative Ideas

### Hide Messages in Songs

1. Generate Morse MIDI from secret message
2. Import into Ableton
3. Layer ultrasonic Morse code over your music
4. Only people with the decoder can read it!

### Multiple Messages

Create different messages on different tracks:

```bash
python text_to_morse_midi.py "TRACK 1" -o track1.mid --dot 0.1
python text_to_morse_midi.py "TRACK 2" -o track2.mid --dot 0.1
```

Use different carrier frequencies:
- Track 1: 19000 Hz
- Track 2: 19500 Hz
- Track 3: 18500 Hz

### Audio Watermarking

Embed your name/copyright in songs:

```bash
python text_to_morse_midi.py "COPYRIGHT 2026 YOUR NAME" -o watermark.mid --dot 0.08
```

Mix at very low level (-18 to -24 dB) - inaudible but detectable!

## ⚙️ Parameter Matching

**Important:** The `--dot` parameter must match between generation and decoding:

**Generation:**
```bash
python text_to_morse_midi.py "TEST" -o test.mid --dot 0.1
```

**In Ableton:** Create audio at 19kHz

**Decoding:**
```bash
python decode_morse.py test.flac --carrier 19000 --dot 0.1
```

## 🔧 Troubleshooting

### Can't see MIDI notes in Ableton

- Make sure you dragged into a **MIDI track**, not an audio track
- Check the MIDI clip is selected
- Zoom in on the piano roll

### Can't hear anything

- **Good!** Ultrasonic is inaudible
- Use Spectrum analyzer to verify the signal
- If you want audible Morse, transpose the synth down

### Decoder says "Carrier is above usable band"

- Your sample rate is too low
- Ableton export settings must be **48kHz or higher**
- Check: Preferences → Audio → Sample Rate

### Low confidence decode

- Check `--dot` parameter matches between generation and decoding
- Verify ultrasonic synth is tuned to exactly 19000 Hz
- Ensure you exported as lossless (WAV/FLAC), not MP3
- Try adjusting threshold: `--threshold 0.4` or `0.6`

## 📊 Recommended Settings

### For Best Decode Results

**Generation:**
```bash
python text_to_morse_midi.py "YOUR MESSAGE" -o message.mid --dot 0.1
```

**Ableton:**
- Synth: Operator with pure sine wave
- Frequency: Exactly 19000 Hz
- Sample rate: 48000 Hz
- Export format: FLAC or WAV

**Decoding:**
```bash
python decode_morse.py output.flac --carrier 19000 --bw 1500 --dot 0.1 --threshold 0.5 --min_bursts 10
```

### For Faster Transmission

**Generation:**
```bash
python text_to_morse_midi.py "QUICK MESSAGE" -o quick.mid --dot 0.06
```

**Decoding:**
```bash
python decode_morse.py output.flac --carrier 19000 --bw 1500 --dot 0.06 --threshold 0.5 --min_bursts 10
```

### For Hidden Messages in Music

**Generation:**
```bash
python text_to_morse_midi.py "SECRET" -o secret.mid --dot 0.08
```

**Ableton:**
- Mix Morse code at -12 dB to -18 dB
- Music at normal level (0 dB)
- Both tracks routed to master

**Decoding:**
```bash
python decode_morse.py song_with_secret.flac --carrier 19000 --bw 1500 --dot 0.08 --threshold 0.55 --min_bursts 10
```

## 🎓 Learning Resources

### Understanding the Workflow

1. **Text** → `text_to_morse_midi.py` → **MIDI file**
2. **MIDI file** → Ableton Live → **Ultrasonic audio (19kHz)**
3. **Audio file** → `decode_morse.py` → **Text** (full circle!)

### ITU Morse Timing

- Dot: 1 unit (e.g., 100ms with `--dot 0.1`)
- Dash: 3 units (300ms)
- Gap within letter: 1 unit (100ms)
- Gap between letters: 3 units (300ms)
- Gap between words: 7 units (700ms)

The script automatically handles all timing - you just set the dot duration!

## 🚀 Quick Reference Card

```bash
# 1. Generate MIDI
python text_to_morse_midi.py "MESSAGE" -o out.mid --dot 0.1

# 2. Import to Ableton → Add Operator sine at 19kHz → Export as FLAC (48kHz)

# 3. Decode
python decode_morse.py out.flac --carrier 19000 --bw 1500 --dot 0.1

# Preview before generating
python text_to_morse_midi.py "MESSAGE" --preview
```

---

**Now you can create ultrasonic Morse code messages in minutes instead of hours! 🎹🎵**
