# Ultrasonic Morse Code Decoder

Decode high-frequency Morse code signals embedded in audio files.

## Usage
```bash
python decode_morse.py audio_file.flac --carrier 19000 --bw 400 --dot 0.014
```

## Requirements
- numpy
- scipy  
- soundfile (for FLAC support)