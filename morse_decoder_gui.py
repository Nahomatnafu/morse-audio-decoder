#!/usr/bin/env python3
"""
Morse Code Decoder GUI
A graphical interface for decoding ultrasonic Morse code from audio files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageTk

# Import the decoder functions from decode_morse.py
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
        raise ValueError("Band edges invalid for given sample rate")
    b, a = butter(4, [low/(sr/2), high/(sr/2)], btype='bandpass')
    return filtfilt(b, a, x)

def envelope(x, sr, win_ms=8):
    rect = np.abs(x)
    win = max(1, int(sr * win_ms/1000.0))
    kernel = np.ones(win)/win
    return np.convolve(rect, kernel, mode="same")

def hysteresis_thresh(x, low, high):
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
    if mask[0]:
        starts = np.r_[0, starts]
    if mask[-1]:
        ends = np.r_[ends, len(mask)]
    on_segments = [(s/sr, e/sr) for s, e in zip(starts, ends)]
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
    def classify_duration(d, units):
        ratios = {name: abs(d - k*dot_s)/(k*dot_s) for name, k in units.items()}
        name, relerr = min(ratios.items(), key=lambda kv: kv[1])
        return (name if relerr <= tol else None), relerr

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
    
    gaps = []
    for i in range(len(on_segments)-1):
        g = on_segments[i+1][0] - on_segments[i][1]
        gaps.append(g)
    for i, g in enumerate(gaps):
        name, _ = classify_duration(g, units_off)
        symbols.insert(2*i+1, ("off", name if name else "unknown", g))

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
            if name == "intra":
                pass
            elif name == "letter":
                morse.append("".join(letter)); letter=[]
            elif name == "word":
                morse.append("".join(letter)); letter=[]
                morse.append("/")
            else:
                unknown += 1
    if letter:
        morse.append("".join(letter))

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


class MorseDecoderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultrasonic Morse Code Decoder")
        self.root.geometry("900x750")
        self.root.resizable(True, True)

        # Set icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'audio_icon.png')
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(True, icon_photo)
        except:
            pass  # Icon not critical

        # Configure modern style with colors
        style = ttk.Style()
        style.theme_use('clam')

        # Define color scheme
        self.colors = {
            'primary': '#2E86AB',      # Blue
            'secondary': '#A23B72',    # Purple
            'success': '#06A77D',      # Green
            'warning': '#F18F01',      # Orange
            'danger': '#C73E1D',       # Red
            'bg_light': '#F4F4F9',     # Light gray
            'bg_dark': '#2C3E50',      # Dark blue-gray
            'text_dark': '#2C3E50',    # Dark text
            'accent': '#6C5CE7',       # Purple accent
        }

        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'),
                       foreground=self.colors['primary'])
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'),
                       foreground=self.colors['text_dark'])
        style.configure('Accent.TButton', font=('Arial', 11, 'bold'),
                       background=self.colors['primary'], foreground='white')
        style.configure('Preset.TButton', font=('Arial', 9),
                       background=self.colors['accent'])

        # Set background color
        self.root.configure(bg=self.colors['bg_light'])

        self.setup_ui()
        
    def setup_ui(self):
        # Main container with colored background
        main_frame = tk.Frame(self.root, bg=self.colors['bg_light'], padx=15, pady=15)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Header frame with icon and title
        header_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=80)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)

        # Load and display icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'audio_icon.png')
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                icon_img = icon_img.resize((60, 60), Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                icon_label = tk.Label(header_frame, image=self.icon_photo,
                                     bg=self.colors['primary'])
                icon_label.grid(row=0, column=0, padx=20, pady=10)
        except:
            pass

        # Title with modern styling
        title_label = tk.Label(header_frame,
                              text="🎵 Ultrasonic Morse Code Decoder",
                              font=('Arial', 20, 'bold'),
                              bg=self.colors['primary'],
                              fg='white')
        title_label.grid(row=0, column=1, sticky=tk.W, pady=10)

        subtitle_label = tk.Label(header_frame,
                                 text="Extract hidden messages from audio files",
                                 font=('Arial', 10),
                                 bg=self.colors['primary'],
                                 fg='#E0E0E0')
        subtitle_label.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # File selection with modern card style
        file_card = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        file_card.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_card.columnconfigure(1, weight=1)

        tk.Label(file_card, text="📁 Audio File:", font=('Arial', 11, 'bold'),
                bg='white', fg=self.colors['text_dark']).grid(row=0, column=0, sticky=tk.W,
                                                               pady=10, padx=10)
        self.file_path = tk.StringVar()
        file_entry = tk.Entry(file_card, textvariable=self.file_path, width=50,
                             font=('Arial', 10), relief=tk.FLAT, bg='#F8F9FA',
                             fg=self.colors['text_dark'])
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10, padx=10)

        browse_btn = tk.Button(file_card, text="📂 Browse", command=self.browse_file,
                              bg=self.colors['accent'], fg='white', font=('Arial', 10, 'bold'),
                              relief=tk.FLAT, padx=15, pady=5, cursor='hand2')
        browse_btn.grid(row=0, column=2, pady=10, padx=10)
        
        # Parameters frame with modern card style
        params_card = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        params_card.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        params_card.columnconfigure(1, weight=1)
        params_card.columnconfigure(3, weight=1)

        # Parameters header
        tk.Label(params_card, text="⚙️ Decoder Parameters", font=('Arial', 12, 'bold'),
                bg='white', fg=self.colors['text_dark']).grid(row=0, column=0, columnspan=4,
                                                               sticky=tk.W, pady=(10, 5), padx=10)

        # Carrier Frequency
        tk.Label(params_card, text="Carrier Frequency (Hz):", bg='white',
                font=('Arial', 9)).grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.carrier_freq = tk.StringVar(value="19000")
        tk.Entry(params_card, textvariable=self.carrier_freq, width=15,
                font=('Arial', 9), relief=tk.FLAT, bg='#F8F9FA').grid(row=1, column=1,
                                                                       sticky=tk.W, padx=5, pady=5)

        # Bandwidth
        tk.Label(params_card, text="Bandwidth (Hz):", bg='white',
                font=('Arial', 9)).grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20,5))
        self.bandwidth = tk.StringVar(value="1500")
        tk.Entry(params_card, textvariable=self.bandwidth, width=15,
                font=('Arial', 9), relief=tk.FLAT, bg='#F8F9FA').grid(row=1, column=3,
                                                                       sticky=tk.W, padx=5, pady=5)

        # Dot Length
        tk.Label(params_card, text="Dot Length (s):", bg='white',
                font=('Arial', 9)).grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        self.dot_length = tk.StringVar(value="0.100")
        tk.Entry(params_card, textvariable=self.dot_length, width=15,
                font=('Arial', 9), relief=tk.FLAT, bg='#F8F9FA').grid(row=2, column=1,
                                                                       sticky=tk.W, padx=5, pady=5)

        # Threshold
        tk.Label(params_card, text="Threshold (0-1):", bg='white',
                font=('Arial', 9)).grid(row=2, column=2, sticky=tk.W, pady=5, padx=(20,5))
        self.threshold = tk.StringVar(value="0.5")
        tk.Entry(params_card, textvariable=self.threshold, width=15,
                font=('Arial', 9), relief=tk.FLAT, bg='#F8F9FA').grid(row=2, column=3,
                                                                       sticky=tk.W, padx=5, pady=5)

        # Min Bursts
        tk.Label(params_card, text="Min Bursts:", bg='white',
                font=('Arial', 9)).grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        self.min_bursts = tk.StringVar(value="10")
        tk.Entry(params_card, textvariable=self.min_bursts, width=15,
                font=('Arial', 9), relief=tk.FLAT, bg='#F8F9FA').grid(row=3, column=1,
                                                                       sticky=tk.W, padx=5, pady=5)

        # Preset buttons with modern styling
        preset_frame = tk.Frame(params_card, bg='white')
        preset_frame.grid(row=3, column=2, columnspan=2, sticky=tk.W, padx=(20,10), pady=5)
        tk.Label(preset_frame, text="Quick Presets:", bg='white',
                font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0,10))

        standard_btn = tk.Button(preset_frame, text="🎯 Standard", command=self.preset_standard,
                                bg=self.colors['success'], fg='white', font=('Arial', 9, 'bold'),
                                relief=tk.FLAT, padx=10, pady=3, cursor='hand2')
        standard_btn.pack(side=tk.LEFT, padx=3)

        music_btn = tk.Button(preset_frame, text="🎵 Music", command=self.preset_music,
                             bg=self.colors['secondary'], fg='white', font=('Arial', 9, 'bold'),
                             relief=tk.FLAT, padx=10, pady=3, cursor='hand2')
        music_btn.pack(side=tk.LEFT, padx=3)

        # Add some padding at bottom
        tk.Label(params_card, text="", bg='white').grid(row=4, column=0, pady=5)
        
        # Decode button with modern styling
        decode_btn = tk.Button(main_frame, text="🔍 DECODE AUDIO", command=self.decode_audio,
                              bg=self.colors['primary'], fg='white', font=('Arial', 13, 'bold'),
                              relief=tk.FLAT, padx=40, pady=12, cursor='hand2',
                              activebackground=self.colors['accent'], activeforeground='white')
        decode_btn.grid(row=3, column=0, columnspan=3, pady=15)

        # Add hover effect
        def on_enter(e):
            decode_btn['background'] = self.colors['accent']
        def on_leave(e):
            decode_btn['background'] = self.colors['primary']
        decode_btn.bind("<Enter>", on_enter)
        decode_btn.bind("<Leave>", on_leave)
        
        # Results frame with modern card style
        results_card = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        results_card.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_card.columnconfigure(0, weight=1)
        results_card.rowconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Results header
        tk.Label(results_card, text="📊 Decoding Results", font=('Arial', 12, 'bold'),
                bg='white', fg=self.colors['text_dark']).grid(row=0, column=0, sticky=tk.W,
                                                               pady=(10, 5), padx=10)

        # Results text area with modern styling
        self.results_text = scrolledtext.ScrolledText(results_card, height=18, width=70,
                                                      font=('Consolas', 10), wrap=tk.WORD,
                                                      bg='#F8F9FA', fg=self.colors['text_dark'],
                                                      relief=tk.FLAT, padx=10, pady=10)
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        
        # Status bar with modern styling
        status_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'], height=35)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 0))

        self.status_var = tk.StringVar(value="✨ Ready to decode audio files...")
        status_bar = tk.Label(status_frame, textvariable=self.status_var,
                             bg=self.colors['bg_dark'], fg='white',
                             font=('Arial', 9), anchor=tk.W, padx=10)
        status_bar.pack(fill=tk.BOTH, expand=True, pady=8)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.flac *.wav *.mp3"),
                ("FLAC Files", "*.flac"),
                ("WAV Files", "*.wav"),
                ("MP3 Files", "*.mp3"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.file_path.set(filename)
            self.status_var.set(f"✅ Selected: {os.path.basename(filename)}")
    
    def preset_standard(self):
        self.carrier_freq.set("19000")
        self.bandwidth.set("1500")
        self.dot_length.set("0.100")
        self.threshold.set("0.5")
        self.min_bursts.set("10")
        self.status_var.set("🎯 Applied Standard preset - Ready to decode!")

    def preset_music(self):
        self.carrier_freq.set("19500")
        self.bandwidth.set("800")
        self.dot_length.set("0.100")
        self.threshold.set("0.55")
        self.min_bursts.set("10")
        self.status_var.set("🎵 Applied Music preset - Ready to decode!")
    
    def decode_audio(self):
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Validate inputs
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select an audio file first!")
            return
        
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("Error", "Selected file does not exist!")
            return
        
        try:
            carrier = float(self.carrier_freq.get())
            bw = float(self.bandwidth.get())
            dot = float(self.dot_length.get())
            thresh = float(self.threshold.get())
            min_b = int(self.min_bursts.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid parameter values! Please check your inputs.")
            return
        
        self.status_var.set("⏳ Decoding... Please wait...")
        self.root.update()

        # Perform decoding
        try:
            result = self.perform_decode(self.file_path.get(), carrier, bw, dot, thresh, min_b)
            self.display_results(result)
            self.status_var.set("✅ Decoding complete!")
        except Exception as e:
            self.results_text.insert(tk.END, f"❌ ERROR: {str(e)}\n\n")
            self.results_text.insert(tk.END, "This could be due to:\n")
            self.results_text.insert(tk.END, "• Unsupported audio format\n")
            self.results_text.insert(tk.END, "• Corrupted audio file\n")
            self.results_text.insert(tk.END, "• Invalid parameter settings\n")
            self.status_var.set("❌ Decoding failed!")
    
    def perform_decode(self, path, carrier, bw, dot, thresh, min_bursts):
        result = {
            'status': 'unknown',
            'file': os.path.basename(path),
            'sample_rate': 0,
            'nyquist': 0,
            'morse': '',
            'text': '',
            'confidence': 0.0,
            'bursts': 0,
            'avg_on_ms': 0.0,
            'dot_param_ms': dot * 1000,
            'message': ''
        }
        
        # Load audio
        try:
            sr, y = load_audio(path)
            result['sample_rate'] = sr
            result['nyquist'] = sr / 2
        except Exception as e:
            result['status'] = 'load_error'
            result['message'] = f"Failed to read audio: {e}"
            return result
        
        # Check if carrier is above Nyquist
        if carrier + bw/2 >= (sr/2 - 100):
            result['status'] = 'carrier_too_high'
            result['message'] = "Carrier is above usable band for this file. This encoding likely removed the ultrasonic signal (expected for low-bitrate MP3)."
            return result
        
        # Filter and envelope
        try:
            yf = bandpass_sig(y, sr, carrier, bw)
        except Exception as e:
            result['status'] = 'filter_error'
            result['message'] = f"Filter error: {e}"
            return result
        
        env = envelope(yf, sr, win_ms=8)
        env = env / (np.max(env) + 1e-9)
        
        # Threshold and segment
        low = thresh * 0.7
        high = thresh
        mask = hysteresis_thresh(env, low, high)
        on_segments, _ = segments_from_mask(mask, sr)
        
        result['bursts'] = len(on_segments)
        
        # Check minimum bursts
        if len(on_segments) < min_bursts:
            result['status'] = 'too_few_bursts'
            duty = np.mean(mask)
            result['message'] = f"No valid Morse pattern detected (too few bursts: {len(on_segments)}).\nDuty cycle: {duty:.2f}, Envelope max: {np.max(env):.2f}"
            return result
        
        # Decode morse
        pieces, unknown = quantize_morse(on_segments, None, dot, tol=0.45)
        morse_str = " ".join(pieces)
        text = decode_morse_pieces(pieces)
        
        # Calculate confidence
        unknown_penalty = unknown / (len(on_segments) + 1e-9)
        avg_on = np.mean([(e - s) for (s, e) in on_segments])
        conf = max(0.0, 1.0 - unknown_penalty) * max(0.0, 1.0 - abs(avg_on - dot*1.8)/(dot*2.5))
        
        result['morse'] = morse_str
        result['text'] = text
        result['confidence'] = conf
        result['avg_on_ms'] = avg_on * 1000
        
        if conf < 0.35 or text == "" or all(ch == "?" for ch in text.replace(" ", "")):
            result['status'] = 'low_confidence'
            result['message'] = "Low confidence—likely not valid Morse (or timing/threshold off)."
        else:
            result['status'] = 'success'
            result['message'] = "Successfully decoded!"
        
        return result
    
    def display_results(self, result):
        self.results_text.insert(tk.END, "=" * 80 + "\n")
        self.results_text.insert(tk.END, f"📁 File: {result['file']}\n")
        self.results_text.insert(tk.END, "=" * 80 + "\n\n")
        
        if result['sample_rate'] > 0:
            self.results_text.insert(tk.END, f"📊 Audio Info:\n")
            self.results_text.insert(tk.END, f"   Sample Rate: {result['sample_rate']} Hz\n")
            self.results_text.insert(tk.END, f"   Nyquist Frequency: {result['nyquist']:.1f} Hz\n\n")
        
        if result['status'] == 'success':
            self.results_text.insert(tk.END, "✅ DECODING SUCCESSFUL!\n\n", 'success')
            self.results_text.insert(tk.END, f"📝 Decoded Message:\n")
            self.results_text.insert(tk.END, f"   {result['text']}\n\n", 'message')
            self.results_text.insert(tk.END, f"🔤 Morse Code:\n")
            self.results_text.insert(tk.END, f"   {result['morse']}\n\n")
            self.results_text.insert(tk.END, f"📈 Statistics:\n")
            self.results_text.insert(tk.END, f"   Confidence: {result['confidence']:.2%}\n")
            self.results_text.insert(tk.END, f"   Bursts Detected: {result['bursts']}\n")
            self.results_text.insert(tk.END, f"   Avg ON Duration: {result['avg_on_ms']:.1f} ms\n")
            self.results_text.insert(tk.END, f"   Dot Parameter: {result['dot_param_ms']:.0f} ms\n")
            
            # Configure tags for colored text
            self.results_text.tag_config('success', foreground=self.colors['success'],
                                         font=('Arial', 12, 'bold'))
            self.results_text.tag_config('message', foreground=self.colors['primary'],
                                         font=('Consolas', 14, 'bold'))
            
        elif result['status'] == 'carrier_too_high':
            self.results_text.insert(tk.END, "⚠️ CARRIER FREQUENCY TOO HIGH\n\n", 'warning')
            self.results_text.insert(tk.END, f"{result['message']}\n\n")
            self.results_text.insert(tk.END, "💡 Tip: This is expected for low-bitrate MP3 files.\n")
            self.results_text.insert(tk.END, "   Try using a FLAC or high-bitrate audio file instead.\n")
            self.results_text.tag_config('warning', foreground=self.colors['warning'],
                                         font=('Arial', 12, 'bold'))
            
        elif result['status'] == 'too_few_bursts':
            self.results_text.insert(tk.END, "⚠️ NO VALID MORSE PATTERN DETECTED\n\n", 'warning')
            self.results_text.insert(tk.END, f"{result['message']}\n\n")
            self.results_text.insert(tk.END, "💡 Suggestions:\n")
            self.results_text.insert(tk.END, "   • Try adjusting the threshold value\n")
            self.results_text.insert(tk.END, "   • Check if the carrier frequency is correct\n")
            self.results_text.insert(tk.END, "   • Reduce the minimum bursts requirement\n")
            self.results_text.insert(tk.END, "   • This file may not contain Morse code\n")
            self.results_text.tag_config('warning', foreground=self.colors['warning'],
                                         font=('Arial', 12, 'bold'))
            
        elif result['status'] == 'low_confidence':
            self.results_text.insert(tk.END, "⚠️ LOW CONFIDENCE DECODING\n\n", 'warning')
            self.results_text.insert(tk.END, f"📝 Decoded (uncertain):\n")
            self.results_text.insert(tk.END, f"   {result['text'] if result['text'] else '(empty)'}\n\n")
            self.results_text.insert(tk.END, f"🔤 Morse Code:\n")
            self.results_text.insert(tk.END, f"   {result['morse']}\n\n")
            self.results_text.insert(tk.END, f"📈 Statistics:\n")
            self.results_text.insert(tk.END, f"   Confidence: {result['confidence']:.2%}\n")
            self.results_text.insert(tk.END, f"   Bursts: {result['bursts']}\n\n")
            self.results_text.insert(tk.END, "💡 Suggestions:\n")
            self.results_text.insert(tk.END, "   • Try adjusting the dot length parameter\n")
            self.results_text.insert(tk.END, "   • Adjust the threshold value\n")
            self.results_text.insert(tk.END, "   • Check carrier frequency and bandwidth settings\n")
            self.results_text.tag_config('warning', foreground=self.colors['warning'],
                                         font=('Arial', 12, 'bold'))

        else:
            self.results_text.insert(tk.END, "❌ DECODING FAILED\n\n", 'error')
            self.results_text.insert(tk.END, f"{result['message']}\n")
            self.results_text.tag_config('error', foreground=self.colors['danger'],
                                         font=('Arial', 12, 'bold'))


def main():
    root = tk.Tk()
    app = MorseDecoderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

