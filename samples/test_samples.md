# Test Samples

This document contains test commands for various audio samples demonstrating the decoder's capabilities.

## FLAC vs MP3 Encoding Test

### 1. FLAC (Lossless - Inaudible Ultrasonic)

```bash
python decode_morse.py "samples/hello_ultrasonic_2.flac" --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.5 --min_bursts 10

python decode_morse.py "samples/test_ultrasonic.flac" --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.5 --min_bursts 6

python decode_morse.py "samples/prompt_ultrasonic.flac" --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.55 --min_bursts 10
```

### 2. MP3 (Lossy - Ultrasonic Removed)

```bash
python decode_morse.py samples/hello_ultrasonic.mp3 --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.5 --min_bursts 10

python decode_morse.py samples/test_ultrasonic.mp3 --carrier 19000 --bw 1500 --dot 0.100 --threshold 0.5 --min_bursts 10
```

### 3. Song Test (Hidden in Music)

```bash
python decode_morse.py "samples/the_ocean_is_real_test.flac" --carrier 19500 --bw 800 --dot 0.100 --threshold 0.55 --min_bursts 10

python decode_morse.py "samples/the_ocean_is_fake_test.flac" --carrier 19500 --bw 800 --dot 0.100 --threshold 0.55 --min_bursts 10
```

## Expected Results

- **FLAC files**: Should decode successfully with high confidence
- **MP3 files**: Should fail with "Carrier is above usable band" message
- **Song tests**: Demonstrate steganographic capabilities