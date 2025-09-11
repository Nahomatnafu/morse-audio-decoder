# decode_morse.py
# Usage:
#   python decode_morse.py path/to/file.flac --carrier 19000 --bw 400 --dot 0.10
# Optional:
#   --sr 44100 --threshold 0.25 --min_bursts 6

import argparse, sys, math
import numpy as np

# Prefer soundfile for FLAC; fall back to scipy for WAV/MP3 via audioread
try:
    import soundfile as sf
    def load_audio(path):
        y, sr = sf.read(path, dtype="float32", always_2d=False)
        if y.ndim == 2:
            y = np.mean(y, axis=1)
        return sr, y
except Exception:
    from scipy.io import wavfile
    def load_audio(path):
        if not path.lower().endswith(".wav"):
            raise RuntimeError("Install 'soundfile' to read non-WAV formats like FLAC/MP3.")
        sr, y = wavfile.read(path)
        y = y.astype(np.float32) / (np.iinfo(y.dtype).max if np.issubdtype(y.dtype, np.integer) else 1.0)
        if y.ndim == 2:
            y = np.mean(y, axis=1)
        return sr, y

from scipy.signal import butter, filtfilt

MORSE_TABLE = {
    ".-":"A","-...":"B","-.-.":"C","-..":"D",".":"E","..-.":"F","--.":"G","....":"H","..":"I",
    ".---":"J","-.-":"K",".-..":"L","--":"M","-.":"N","---":"O",".--.":"P","--.-":"Q",".-.":"R",
    "...":"S","-":"T","..-":"U","...-":"V",".--":"W","-..-":"X","-.--":"Y","--..":"Z",
    "-----":"0",".----":"1","..---":"2","...--":"3","....-":"4",".....":"5","-....":"6",
    "--...":"7","---..":"8","----.":"9"
}

def bandpass_sig(x, sr, center_hz, bw_hz):
    low = max(1.0, center_hz - bw_hz/2.0)
    high = min(sr/2.0 - 100.0, center_hz + bw_hz/2.0)
    if not (0 < low < high < sr/2):
        raise ValueError("Band edges invalid for given sample rate; lower your --carrier or --bw.")
    b, a = butter(4, [low/(sr/2), high/(sr/2)], btype='bandpass')
    return filtfilt(b, a, x)

def envelope(x, sr, win_ms=8):
    rect = np.abs(x)
    win = max(1, int(sr * win_ms/1000.0))
    kernel = np.ones(win)/win
    return np.convolve(rect, kernel, mode="same")

def hysteresis_thresh(x, low, high):
    # returns boolean mask of "on" using simple hysteresis
    on = np.zeros_like(x, dtype=bool)
    state = False
    for i, v in enumerate(x):
        if not state and v >= high:
            state = True
        elif state and v <= low:
            state = False
        on[i] = state
    return on

def segments_from_mask(mask, sr):
    edges = np.diff(mask.astype(np.int8))
    starts = np.where(edges == 1)[0] + 1
    ends   = np.where(edges == -1)[0] + 1
    if mask[0]:  # started inside a segment
        starts = np.r_[0, starts]
    if mask[-1]:
        ends = np.r_[ends, len(mask)]
    on_segments = [(s/sr, e/sr) for s, e in zip(starts, ends)]
    # OFF segments are gaps between ON segments
    off_segments = []
    last = 0
    for s, e in zip(starts, ends):
        if s > last:
            off_segments.append((last/sr, s/sr))
        last = e
    if last < len(mask):
        off_segments.append((last/sr, len(mask)/sr))
    return on_segments, off_segments

def quantize_morse(on_segments, off_segments, dot_s, tol=0.4):
    # ITU: dash = 3 dots; intra-char gap = 1 dot; letter gap = 3 dots; word gap = 7 dots
    def classify_duration(d, units):
        # return closest unit name if within tolerance
        ratios = {name: abs(d - k*dot_s)/(k*dot_s) for name, k in units.items()}
        name, relerr = min(ratios.items(), key=lambda kv: kv[1])
        return (name if relerr <= tol else None), relerr

    # Build symbol stream: alternate ON (dot/dash) and OFF (gaps)
    units_on  = {"dot":1, "dash":3}
    units_off = {"intra":1, "letter":3, "word":7}

    symbols = []
    for (s,e) in on_segments:
        d = e - s
        name, _ = classify_duration(d, units_on)
        if name is None:
            symbols.append(("on","unknown",d))
        else:
            symbols.append(("on",name,d))
        # matching OFF after it (except the last)
        # (We derive OFF durations from the actual gaps between ONs)
    # Now compute OFFs from consecutive ONs:
    gaps = []
    for i in range(len(on_segments)-1):
        g = on_segments[i+1][0] - on_segments[i][1]
        gaps.append(g)
    for i, g in enumerate(gaps):
        name, _ = classify_duration(g, units_off)
        symbols.insert(2*i+1, ("off", name if name else "unknown", g))

    # Convert to morse string with . - and separators
    morse = []
    letter = []
    unknown = 0
    for typ, name, d in symbols:
        if typ == "on":
            if name == "dot": letter.append(".")
            elif name == "dash": letter.append("-")
            else:
                unknown += 1
        else:
            if name == "intra":  # same letter
                pass
            elif name == "letter":
                morse.append("".join(letter)); letter=[]
            elif name == "word":
                morse.append("".join(letter)); letter=[]
                morse.append("/")  # word separator
            else:
                unknown += 1
    if letter:
        morse.append("".join(letter))

    # Collapse empty pieces
    morse_clean = [m for m in morse if m != ""]
    return morse_clean, unknown

def decode_morse_pieces(pieces):
    words, current = [], []
    for p in pieces:
        if p == "/":
            if current:
                words.append(current); current=[]
            else:
                words.append([])
        else:
            current.append(p)
    if current: words.append(current)

    out = []
    for letters in words:
        txt = "".join(MORSE_TABLE.get(l,"?") for l in letters)
        out.append(txt)
    return " ".join(out).strip()

def main():
    ap = argparse.ArgumentParser(description="Decode high-freq Morse from audio.")
    ap.add_argument("path", help="Audio file (FLAC/WAV/MP3 if supported).")
    ap.add_argument("--carrier", type=float, default=19000.0, help="Carrier frequency Hz (default 19000).")
    ap.add_argument("--bw", type=float, default=400.0, help="Bandpass width Hz (default 400).")
    ap.add_argument("--dot", type=float, default=0.10, help="Dot length seconds (default 0.10).")
    ap.add_argument("--sr", type=int, default=None, help="(Optional) resample target Hz (not implemented; keep None).")
    ap.add_argument("--threshold", type=float, default=0.25, help="Envelope threshold fraction of max (0-1).")
    ap.add_argument("--min_bursts", type=int, default=6, help="Minimum ON bursts to consider valid.")
    args = ap.parse_args()

    try:
        sr, y = load_audio(args.path)
        print(f"[i] Loaded {args.path} | Sample rate: {sr} Hz | Nyquist: {sr/2:.1f} Hz")
        # Guard: if carrier band exceeds Nyquist (common for low-bitrate/low-SR MP3), exit gracefully
        if args.carrier + args.bw/2 >= (sr/2 - 100):
            print("Result: Carrier is above usable band for this file. "
                  "This encoding likely removed the ultrasonic signal (expected for low-bitrate MP3).")
            sys.exit(0)
    except Exception as e:
        print(f"[!] Failed to read audio: {e}")
        sys.exit(1)


    # Filter around carrier and compute envelope
    try:
        yf = bandpass_sig(y, sr, args.carrier, args.bw)
    except Exception as e:
        print(f"[!] Filter error: {e}")
        sys.exit(1)

    env = envelope(yf, sr, win_ms=8)
    env = env / (np.max(env) + 1e-9)

    # Hysteresis thresholds for stability
    low = args.threshold * 0.7
    high = args.threshold
    mask = hysteresis_thresh(env, low, high)
    on_segments, _ = segments_from_mask(mask, sr)

    # Quick sanity: if it’s just one long tone, reject
    if len(on_segments) < args.min_bursts:
        print("Result: no valid Morse pattern detected (too few bursts).")
        # Diagnostics
        duty = np.mean(mask)
        print(f"Diagnostics: bursts={len(on_segments)}, duty_cycle={duty:.2f}, env_max={np.max(env):.2f}")
        sys.exit(0)

    pieces, unknown = quantize_morse(on_segments, None, args.dot, tol=0.45)
    morse_str = " ".join(pieces)
    text = decode_morse_pieces(pieces)

    # Confidence metric: proportion of recognized items and timing consistency
    total_items = max(1, len(pieces))
    unknown_penalty = unknown / (len(on_segments) + 1e-9)
    avg_on = np.mean([(e - s) for (s, e) in on_segments])
    conf = max(0.0, 1.0 - unknown_penalty) * max(0.0, 1.0 - abs(avg_on - args.dot*1.8)/(args.dot*2.5))

    print("Decoded:")
    print(f"  Morse : {morse_str}")
    print(f"  Text  : {text if text else '(empty)'}")
    print(f"  Confidence: {conf:.2f}")
    print(f"  Bursts: {len(on_segments)}  Avg ON: {avg_on*1000:.1f} ms  Dot param: {args.dot*1000:.0f} ms")

    if conf < 0.35 or text == "" or all(ch == "?" for ch in text):
        print("Result: low confidence—likely not valid Morse (or timing/threshold off).")

if __name__ == "__main__":
    main()
