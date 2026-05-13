# Morse Decoder GUI - User Guide

## Overview
The **Ultrasonic Morse Code Decoder GUI** provides a user-friendly graphical interface for decoding hidden Morse code messages embedded in audio files at ultrasonic frequencies.

## Features

### 🎯 Main Capabilities
- **Drag-and-drop file selection** for audio files (FLAC, WAV, MP3)
- **Adjustable parameters** for fine-tuning the decoder
- **Preset configurations** for common use cases
- **Detailed results display** with color-coded status messages
- **Comprehensive error handling** with helpful suggestions

### 📊 Supported Formats
- ✅ **FLAC** (Recommended - preserves ultrasonic content)
- ✅ **WAV** (Lossless format)
- ⚠️ **MP3** (May lose ultrasonic content depending on bitrate)

## How to Use

### 1. Launch the Application
```bash
python morse_decoder_gui.py
```

### 2. Select an Audio File
- Click the **"Browse"** button
- Navigate to your audio file
- Select a FLAC, WAV, or MP3 file

### 3. Configure Parameters

#### Quick Start - Use Presets:
- **Standard Preset**: For basic ultrasonic Morse code
  - Carrier: 19000 Hz
  - Bandwidth: 1500 Hz
  - Dot Length: 0.100 s
  - Threshold: 0.5
  - Min Bursts: 10

- **Music Preset**: For signals hidden in music
  - Carrier: 19500 Hz
  - Bandwidth: 800 Hz
  - Dot Length: 0.100 s
  - Threshold: 0.55
  - Min Bursts: 10

#### Advanced - Manual Configuration:

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| **Carrier Frequency** | Center frequency of the ultrasonic signal | 18000-20000 Hz |
| **Bandwidth** | Width of the frequency band to analyze | 400-1500 Hz |
| **Dot Length** | Duration of a Morse code dot in seconds | 0.01-0.15 s |
| **Threshold** | Signal detection sensitivity (0=sensitive, 1=strict) | 0.25-0.7 |
| **Min Bursts** | Minimum signal bursts required for valid decode | 6-15 |

### 4. Decode
Click the **"🔍 Decode Audio"** button and wait for results.

## Understanding Results

### ✅ Success
```
✅ DECODING SUCCESSFUL!

📝 Decoded Message:
   HELLO CHATGPT ARE YOU READY

🔤 Morse Code:
   .... . .-.. .-.. --- / -.-. .... .- - --. .--. - / .- .-. . / -.-- --- ..- / .-. . .- -.. -.--

📈 Statistics:
   Confidence: 98%
   Bursts Detected: 64
   Avg ON Duration: 184.3 ms
   Dot Parameter: 100 ms
```

### ⚠️ Carrier Too High (MP3 Issue)
```
⚠️ CARRIER FREQUENCY TOO HIGH

Carrier is above usable band for this file. This encoding likely removed 
the ultrasonic signal (expected for low-bitrate MP3).

💡 Tip: This is expected for low-bitrate MP3 files.
   Try using a FLAC or high-bitrate audio file instead.
```

**What this means**: The MP3 compression removed frequencies above ~11 kHz, eliminating the ultrasonic signal.

### ⚠️ No Valid Pattern
```
⚠️ NO VALID MORSE PATTERN DETECTED

No valid Morse pattern detected (too few bursts: 1).
Duty cycle: 0.00, Envelope max: 1.00

💡 Suggestions:
   • Try adjusting the threshold value
   • Check if the carrier frequency is correct
   • Reduce the minimum bursts requirement
   • This file may not contain Morse code
```

**What this means**: Either the file doesn't contain Morse code, or the parameters need adjustment.

### ⚠️ Low Confidence
```
⚠️ LOW CONFIDENCE DECODING

📝 Decoded (uncertain):
   SE EEI EI EE E I EEEE  EI EE E

Confidence: 0%

💡 Suggestions:
   • Try adjusting the dot length parameter
   • Adjust the threshold value
   • Check carrier frequency and bandwidth settings
```

**What this means**: A signal was detected but doesn't match valid Morse code patterns well.

## Troubleshooting

### Problem: "Carrier is above usable band"
**Solution**: 
- Use FLAC files instead of MP3
- If using MP3, ensure it's high-bitrate (320kbps) with 48kHz sample rate

### Problem: "Too few bursts detected"
**Solutions**:
1. Lower the threshold (try 0.3-0.4)
2. Reduce min_bursts to 5-6
3. Adjust carrier frequency (try ±500 Hz)
4. Increase bandwidth to 2000 Hz

### Problem: "Low confidence decoding"
**Solutions**:
1. Adjust dot length (try 0.08-0.12)
2. Fine-tune threshold (±0.1)
3. Try different carrier frequencies
4. Check if the file actually contains Morse code

### Problem: Garbled output with question marks
**Solutions**:
1. The timing parameters are off - adjust dot length
2. Try the opposite preset (Standard ↔ Music)
3. Manually adjust parameters in small increments

## Tips for Best Results

1. **Always use FLAC files** when possible for ultrasonic content
2. **Start with presets** before manual tuning
3. **Check the sample rate** - needs to be ≥44.1kHz for 19kHz carrier
4. **Adjust one parameter at a time** when troubleshooting
5. **Look at confidence scores** - above 80% is excellent, below 35% is unreliable

## Sample Files Included

Test the GUI with these sample files in the `samples/` folder:

| File | Expected Result | Preset |
|------|----------------|--------|
| `hello_ultrasonic_2.flac` | "HELLO" | Standard |
| `test_ultrasonic.flac` | "TEST" | Standard |
| `prompt_ultrasonic.flac` | "HELLO CHATGPT ARE YOU READY" | Standard |
| `the_ocean_is_fake_test.flac` | "HELLO CHATGPT ARE YOU READY" | Music |
| `hello_ultrasonic.mp3` | Carrier too high (expected) | Standard |

## Technical Details

### How It Works
1. **Load Audio**: Reads the audio file and extracts mono signal
2. **Bandpass Filter**: Isolates the ultrasonic carrier frequency
3. **Envelope Detection**: Extracts the amplitude modulation (Morse code)
4. **Thresholding**: Identifies ON/OFF bursts using hysteresis
5. **Morse Decoding**: Classifies bursts as dots/dashes and decodes to text
6. **Confidence Calculation**: Evaluates timing consistency and pattern validity

### Why Ultrasonic?
- Frequencies above ~18kHz are **inaudible to humans**
- Allows **steganographic** embedding in music/audio
- **Lossless formats** (FLAC) preserve these frequencies
- **Lossy formats** (MP3) often remove them to save space

## For Your Presentation

### Key Demo Points:
1. **Show successful decode** with `prompt_ultrasonic.flac`
2. **Demonstrate MP3 limitation** with `hello_ultrasonic.mp3`
3. **Explain steganography** - hidden messages in music
4. **Show parameter adjustment** - how threshold affects detection
5. **Discuss applications** - covert communication, watermarking, etc.

### Talking Points:
- "This demonstrates how digital audio can carry hidden information"
- "MP3 compression removes 'unnecessary' high frequencies, destroying the signal"
- "FLAC preserves all frequencies, making it ideal for ultrasonic steganography"
- "The decoder uses signal processing techniques: filtering, envelope detection, and pattern matching"
- "Real-world applications: audio watermarking, broadcast signaling, accessibility features"

## Requirements

```bash
pip install numpy scipy soundfile tkinter
```

Note: `tkinter` is usually included with Python installations.

## License & Credits

Created for Computer Science Presentation
Demonstrates ultrasonic steganography and signal processing concepts

