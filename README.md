# Ultrasonic Morse Code Decoder

A Python-based decoder that extracts hidden Morse code messages embedded at ultrasonic frequencies (18-20 kHz) in audio files. The project demonstrates steganographic techniques by hiding inaudible signals in audio that can be recovered through digital signal processing.

## 🎯 Features

- **Ultrasonic Signal Processing** - Decode messages hidden at frequencies above human hearing range (~19 kHz)
- **Multiple Audio Format Support** - Works with FLAC, WAV, and high-bitrate MP3 files
- **Two Interfaces** - Command-line tool for scripting or GUI for interactive use
- **Configurable Parameters** - Adjust carrier frequency, bandwidth, timing, and thresholds
- **Confidence Scoring** - Evaluates decode accuracy with percentage confidence
- **Format Detection** - Automatically detects when audio formats don't support ultrasonic frequencies

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [GUI Usage](#gui-usage)
- [Command-Line Usage](#command-line-usage)
- [Sample Files](#sample-files)
- [How It Works](#how-it-works)
- [Parameters Explained](#parameters-explained)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

## 🚀 Installation

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)

### Step 1: Clone or Download the Repository

```bash
# If using git
git clone https://github.com/yourusername/morse-audio-decoder.git
cd morse-audio-decoder

# Or download and extract the ZIP file, then navigate to the folder
cd "High Frequency Morse Code"
```

### Step 2: Create a Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt when the environment is activated.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `numpy` - Numerical computing
- `scipy` - Signal processing functions
- `soundfile` - Audio file I/O (FLAC/WAV support)
- `Pillow` - Image processing for GUI icon

### Step 4: Verify Installation

```bash
python decode_morse.py --help
```

If you see the help message, installation was successful!

## ⚡ Quick Start

### Option 1: GUI (Recommended for Beginners)

```bash
python morse_decoder_gui.py
```

1. Click **"📂 Browse"** and select `samples/hello_ultrasonic_2.flac`
2. Click **"🎯 Standard"** preset button
3. Click **"🔍 DECODE AUDIO"**
4. See the decoded message: **"HELLO"** with 91% confidence!

### Option 2: Command-Line

```bash
python decode_morse.py samples/hello_ultrasonic_2.flac --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.5 --min_bursts 10
```

Expected output:
```
[i] Loaded samples/hello_ultrasonic_2.flac | Sample rate: 48000 Hz | Nyquist: 24000.0 Hz
Decoded:
  Morse : .... . .-.. .-.. ---
  Text  : HELLO
  Confidence: 0.91
  Bursts: 16  Avg ON: 158.7 ms  Dot param: 100 ms
```

## 🎨 GUI Usage

### Launch the GUI

```bash
python morse_decoder_gui.py
```

### Interface Overview

The GUI features a modern, color-coded interface with:

- **Header** - Audio icon and title
- **File Selection Card** - Browse and select audio files
- **Parameters Card** - Configure decoding settings
- **Preset Buttons** - Quick configuration for common scenarios
- **Decode Button** - Start the decoding process
- **Results Card** - Color-coded output display
- **Status Bar** - Real-time status updates

### Using Presets

**🎯 Standard Preset** (for basic ultrasonic Morse code):
- Carrier: 19000 Hz
- Bandwidth: 1500 Hz
- Dot Length: 0.100 s
- Threshold: 0.5
- Min Bursts: 10

**🎵 Music Preset** (for signals hidden in music):
- Carrier: 19500 Hz
- Bandwidth: 800 Hz
- Dot Length: 0.100 s
- Threshold: 0.55
- Min Bursts: 10

### Result Interpretation

- **✅ Green** = Successful decode with high confidence
- **⚠️ Orange** = Warning (carrier too high, low confidence, or no pattern)
- **❌ Red** = Error (file not found, corrupted, etc.)

### GUI Features

- **Hover Effects** - Buttons change color when you hover
- **File Browser** - Easy point-and-click file selection
- **Auto-Detection** - Detects MP3 compression issues
- **Helpful Suggestions** - Provides troubleshooting tips
- **Color-Coded Status** - Emoji indicators for different states

## 💻 Command-Line Usage

### Basic Syntax

```bash
python decode_morse.py <audio_file> [options]
```

### Required Argument

- `audio_file` - Path to the audio file (FLAC, WAV, or MP3)

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--carrier` | 19000.0 | Carrier frequency in Hz |
| `--bw` | 400.0 | Bandpass filter bandwidth in Hz |
| `--dot` | 0.10 | Dot length in seconds |
| `--threshold` | 0.25 | Envelope threshold (0-1) |
| `--min_bursts` | 6 | Minimum signal bursts required |

### Example Commands

**Decode a simple message:**
```bash
python decode_morse.py samples/test_ultrasonic.flac --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.5 --min_bursts 6
```

**Decode a complex message:**
```bash
python decode_morse.py samples/prompt_ultrasonic.flac --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.55 --min_bursts 10
```

**Test MP3 limitation:**
```bash
python decode_morse.py samples/hello_ultrasonic.mp3 --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.5 --min_bursts 10
```
Expected: "Carrier is above usable band" (demonstrates MP3 removes ultrasonic content)

## 📁 Sample Files

The `samples/` folder contains test audio files:

| File | Expected Message | Format | Notes |
|------|-----------------|--------|-------|
| `hello_ultrasonic.flac` | HELLO | FLAC | Simple test |
| `hello_ultrasonic_2.flac` | HELLO | FLAC | Alternative encoding |
| `test_ultrasonic.flac` | TEST | FLAC | Short message |
| `prompt_ultrasonic.flac` | HELLO CHATGPT ARE YOU READY | FLAC | Complex message |
| `the_ocean_is_fake_test.flac` | HELLO CHATGPT ARE YOU READY | FLAC | Hidden in music |
| `hello_ultrasonic.mp3` | *(fails)* | MP3 | Low-bitrate - no ultrasonic |
| `hello_ultrasonic_2.mp3` | *(fails)* | MP3 | Low-bitrate - no ultrasonic |
| `test_ultrasonic.mp3` | *(fails)* | MP3 | Low-bitrate - no ultrasonic |
| `prompt_ultrasonic.mp3` | HELLO CHATGPT ARE YOU READY | MP3 | High-bitrate - works! |

### Testing All Samples

See `samples/test_samples.md` for complete test commands for all sample files.

## 🔬 How It Works

### Signal Processing Pipeline

1. **Audio Loading** - Read audio file and convert to mono if stereo
2. **Bandpass Filtering** - Isolate the carrier frequency band (e.g., 18.5-19.5 kHz)
3. **Envelope Detection** - Extract amplitude modulation (the Morse code pattern)
4. **Thresholding** - Convert analog signal to binary ON/OFF states using hysteresis
5. **Segmentation** - Identify timing of ON (signal) and OFF (silence) periods
6. **Morse Decoding** - Classify segments as dots (1 unit), dashes (3 units), and gaps
7. **Text Conversion** - Translate Morse code to readable text using ITU Morse table

### Why Ultrasonic?

- **Inaudible** - Frequencies above ~18 kHz are beyond human hearing range
- **Steganographic** - Hidden messages can be embedded in music/audio
- **Preserved in Lossless Formats** - FLAC/WAV maintain full frequency spectrum
- **Removed by Lossy Compression** - MP3 often removes "unnecessary" high frequencies

### Technical Details

- **Morse Timing** - Based on ITU standard (dash = 3 dots, letter gap = 3 dots, word gap = 7 dots)
- **Hysteresis Thresholding** - Prevents noise-induced flickering
- **Confidence Calculation** - Based on timing consistency and pattern recognition
- **Nyquist Frequency** - Sample rate must be ≥2× carrier frequency (minimum 38 kHz for 19 kHz carrier)

## ⚙️ Parameters Explained

### Carrier Frequency (`--carrier`)
The center frequency of the ultrasonic signal in Hz. Typical range: 18000-20000 Hz.

- **19000 Hz** (default) - Standard ultrasonic frequency, above human hearing
- **19500 Hz** - Alternative frequency to avoid interference
- **Lower values** - May be audible to some people
- **Higher values** - May exceed Nyquist frequency for some audio formats

### Bandwidth (`--bw`)
The width of the frequency band to analyze in Hz. Typical range: 400-2000 Hz.

- **400 Hz** - Narrow band, good for clean signals
- **1500 Hz** - Wider band, more robust to frequency drift
- **Wider = More noise tolerance**, but also more background noise
- **Narrower = Cleaner signal**, but requires precise carrier frequency

### Dot Length (`--dot`)
Duration of a Morse code dot in seconds. Typical range: 0.01-0.15 s.

- **0.100 s** (100 ms) - Standard speed
- **0.014 s** (14 ms) - Fast transmission
- **Too small** - May miss dots or misclassify as noise
- **Too large** - May merge dots and dashes

### Threshold (`--threshold`)
Signal detection sensitivity as a fraction of maximum envelope (0-1).

- **0.25** (default) - Low threshold, more sensitive
- **0.50** - Medium threshold, balanced
- **0.70** - High threshold, only strong signals
- **Too low** - May detect noise as signal
- **Too high** - May miss weak signals

### Minimum Bursts (`--min_bursts`)
Minimum number of signal bursts required to consider valid Morse code.

- **6** (default) - Allows short messages like "TEST"
- **10** - Requires longer messages, filters noise better
- **Higher values** - More confident decodes, but rejects short messages
- **Lower values** - Accepts shorter messages, but may false-positive on noise

## 🔧 Troubleshooting

### "Carrier is above usable band"

**Problem:** The MP3 file's sample rate is too low for the carrier frequency.

**Solution:**
- Use FLAC or WAV files instead of MP3
- If MP3 required, ensure high-bitrate (320 kbps) with 48 kHz sample rate
- Lower the carrier frequency (not recommended as it may be audible)

### "No valid Morse pattern detected (too few bursts)"

**Problem:** The signal wasn't detected or the file doesn't contain Morse code.

**Solutions:**
1. Lower the `--threshold` value (try 0.3 or 0.25)
2. Reduce `--min_bursts` (try 5 or 6)
3. Adjust `--carrier` frequency (±500 Hz)
4. Increase `--bw` bandwidth (try 1500 or 2000)
5. Verify the file actually contains ultrasonic Morse code

### "Low confidence—likely not valid Morse"

**Problem:** Signal detected but timing doesn't match Morse code patterns.

**Solutions:**
1. Adjust `--dot` length (try ±20%: if 0.100, try 0.080-0.120)
2. Fine-tune `--threshold` (try ±0.1)
3. Try the opposite preset in GUI (Standard ↔ Music)
4. Check if the carrier frequency is correct

### Garbled Output with Question Marks

**Problem:** Detected Morse patterns don't match valid characters.

**Solutions:**
1. Timing parameters are incorrect - adjust `--dot` length
2. Try different carrier frequencies
3. Signal may be corrupted or have multiple overlapping transmissions

### GUI Won't Launch

**Problem:** GUI window doesn't appear or crashes.

**Solutions:**
1. Ensure Pillow is installed: `pip install Pillow`
2. Check if tkinter is available: `python -c "import tkinter"`
3. On Linux, install tkinter: `sudo apt-get install python3-tk`
4. Use command-line version as alternative

### Long Delay Before GUI Opens (6-7 seconds)

**Explanation:** This is normal! NumPy and SciPy are large libraries that take time to load.

**Solutions:**
- Launch the GUI before your presentation
- Keep it open between decodes
- This is a one-time startup cost

## 📂 Project Structure

```
High Frequency Morse Code/
├── decode_morse.py              # Command-line decoder
├── morse_decoder_gui.py         # Graphical interface
├── requirements.txt             # Python dependencies
├── audio_icon.png              # GUI icon
├── README.md                   # This file
├── GUI_README.md               # Detailed GUI documentation
├── GUI_FEATURES.md             # GUI design documentation
├── QUICK_START.md              # Quick demo guide
├── TEST_NEW_GUI.md             # GUI testing guide
└── samples/                    # Test audio files
    ├── test_samples.md         # Sample file documentation
    ├── hello_ultrasonic.flac
    ├── hello_ultrasonic_2.flac
    ├── test_ultrasonic.flac
    ├── prompt_ultrasonic.flac
    ├── the_ocean_is_fake_test.flac
    ├── the_ocean_is_real_test.flac
    └── *.mp3                   # MP3 versions of above
```

## 🎓 Educational Use

This project demonstrates:

- **Digital Signal Processing** - Filtering, envelope detection, thresholding
- **Steganography** - Hiding information in plain sight
- **Audio Compression** - Differences between lossy and lossless formats
- **Pattern Recognition** - Morse code timing analysis
- **GUI Development** - Modern interface design with Python/Tkinter
- **Software Engineering** - Modular code, error handling, documentation

## 🚀 Use Cases

- **Audio Watermarking** - Copyright protection and content authentication
- **Covert Communication** - Hidden messaging in audio/music
- **Broadcast Signaling** - Automated system triggers
- **Educational Demonstrations** - Teaching signal processing and steganography
- **Accessibility Features** - Machine-readable audio markers

## 📚 Additional Documentation

- **GUI_README.md** - Complete GUI user guide with troubleshooting
- **QUICK_START.md** - 30-second demo guide and presentation script
- **GUI_FEATURES.md** - Modern GUI design features and color scheme
- **TEST_NEW_GUI.md** - Interactive testing guide for the GUI
- **samples/test_samples.md** - Test commands for all sample files

## 🤝 Contributing

This is an educational/research project. Suggestions and improvements are welcome!

## 📜 License

This project is created for educational purposes as part of a Computer Science research presentation.

## 🙋 FAQ

**Q: Can this decode any audio file?**
A: No, only files that were specifically encoded with ultrasonic Morse code.

**Q: Why doesn't it work with my MP3 files?**
A: Most MP3 encoders remove frequencies above 16-18 kHz to save space. Use FLAC or WAV.

**Q: Can I hear the ultrasonic signal?**
A: No, frequencies above ~18 kHz are beyond the range of human hearing (20 Hz - 20 kHz).

**Q: How were the sample files created?**
A: Using audio synthesis tools to generate sine waves modulated with Morse code at ultrasonic frequencies.

**Q: Is this secure for real covert communication?**
A: No, it's easily detectable with spectrum analysis. This is for educational purposes.

**Q: What sample rate do I need?**
A: Minimum 2× the carrier frequency (Nyquist theorem). For 19 kHz, you need at least 38 kHz sample rate. Standard 44.1 kHz or 48 kHz works well.

## 📧 Contact

For questions about this project, please open an issue on GitHub or contact your course instructor.

---

**Made with 🎵 for Computer Science Research Symposium**