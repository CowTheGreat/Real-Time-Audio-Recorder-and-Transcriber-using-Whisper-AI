import warnings
import torch
from tkinter import simpledialog

# Suppress specific warning
warnings.filterwarnings(
    "ignore",
    message=(
        "You are using `torch.load` with `weights_only=False`.*"
    ),
)

import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from recorder import AudioRecorder
from transcriber import AudioTranscriber
from emotion_analyzer import EmotionAnalyzer
import logging
import os

# Suppress FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class TextBoxLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)

# Set default save directory to the current working directory
save_directory = os.getcwd()
logging.info(f"Default save directory set to: {save_directory}")

def browse_directory(event=None):
    global save_directory
    directory = filedialog.askdirectory(title="Select Directory")
    if directory:
        save_directory = directory
        logging.info(f"Save directory selected: {save_directory}")
    else:
        logging.info(f"No directory selected. Using default: {save_directory}")

def start_recording(event=None):
    if not save_directory:
        logging.warning("Save directory is not set. Please select a directory first.")
        return
    
    recorder.set_save_directory(save_directory)
    try:
        recorder.start_recording()
        start_button.config(state=DISABLED)
        stop_button.config(state=NORMAL)
        transcribe_button.config(state=DISABLED)
        rename_audio_button.config(state=DISABLED)
        rename_transcription_button.config(state=DISABLED)
        analyze_button.config(state=DISABLED)  # Disable emotion analysis button

        transcription_box.delete(1.0, tk.END)  # Clear previous transcription
        logging.info("Start recording button clicked")
    except RuntimeError as e:
        logging.error(e)
        log_box.config(state=tk.NORMAL)
        log_box.insert(tk.END, f"Error: {e}\n")
        log_box.config(state=tk.DISABLED)

def stop_recording(event=None):
    recorder.stop_recording()
    start_button.config(state=NORMAL)
    stop_button.config(state=DISABLED)
    transcribe_button.config(state=NORMAL)
    rename_audio_button.config(state=NORMAL)
    logging.info("Stop recording button clicked")

def transcribe_audio(event=None):
    if not recorder.filepath:
        logging.warning("No audio file available for transcription.")
        transcription_box.insert(tk.END, "No audio file available for transcription.\n")
        return
    
    # Clear previous transcription
    transcription_box.delete(1.0, tk.END)
    # Get transcription
    transcription = transcriber.transcribe_audio(recorder.filepath, save_directory)
    analyze_button.config(state=NORMAL)  # Enable emotion analysis after transcription

    # Check for errors and handle transcription
    if not transcription.startswith("Error:"):
        # Save transcription to file
        if transcriber.save_transcription(transcription, save_directory):
            # Enable rename button only if save was successful
            rename_transcription_button.config(state=NORMAL)
        
        # Display transcription in text box
        transcription_box.delete(1.0, tk.END)  # Clear again to be safe
        transcription_box.insert(tk.END, transcription)
        logging.info("Transcription displayed in the UI.")
    else:
        # If there was an error, display it and disable rename button
        transcription_box.insert(tk.END, transcription)
        rename_transcription_button.config(state=DISABLED)
        logging.error("Failed to transcribe audio")

def rename_audio_file(event=None):
    if not recorder.filepath:
        logging.warning("No audio file available to rename.")
        return
    
    new_name = simpledialog.askstring("Rename Audio File", "Enter new filename (without extension):")
    if new_name:
        if recorder.rename_audio(new_name):
            logging.info(f"Audio file renamed successfully to {new_name}.wav")
        else:
            logging.error("Failed to rename audio file")

def rename_transcription_file(event=None):
    if not transcriber.transcription_file:
        logging.warning("No transcription file available to rename.")
        return
    
    new_name = simpledialog.askstring("Rename Transcription File", "Enter new filename (without extension):")
    if new_name:
        if transcriber.rename_transcription(new_name):
            logging.info(f"Transcription file renamed successfully to {new_name}_transcription.txt")
        else:
            logging.error("Failed to rename transcription file")

    analyze_button.config(state=NORMAL)  # Enable emotion analysis after transcription
    logging.info("Transcription displayed in the UI.")

def analyze_emotions(event=None):
    if not recorder.filepath or not os.path.exists(recorder.filepath):
        logging.warning("No audio file available for emotion analysis.")
        transcription_box.insert(tk.END, "\nNo audio file available for emotion analysis.")
        return
    
    try:
        # Get the current transcription text
        current_text = transcription_box.get("1.0", tk.END).strip()
        if not current_text:
            logging.warning("No transcription available for emotion analysis.")
            return
            
        # Remove the "Transcription:" prefix if it exists
        if current_text.startswith("Transcription:"):
            current_text = current_text.replace("Transcription:", "", 1).strip()
            
        # Perform emotion analysis
        emotion_analysis = emotion_analyzer.analyze(current_text, recorder.filepath)
        
        # Save emotion analysis
        if save_directory:
            emotion_path = os.path.join(save_directory, "emotion_analysis.txt")
        else:
            emotion_path = "emotion_analysis.txt"
            
        with open(emotion_path, "w", encoding="utf-8") as f:
            f.write(f"Emotion Analysis:\n{emotion_analysis}")
        
        # Display in UI
        transcription_box.insert(tk.END, "\n\nEmotion Analysis:\n" + emotion_analysis)
        logging.info(f"Emotion analysis completed and saved to {emotion_path}")
        
    except Exception as e:
        logging.error(f"Error during emotion analysis: {e}")
        transcription_box.insert(tk.END, f"\nError during emotion analysis: {e}")

# Initialize recorder, transcriber, and emotion analyzer
recorder = AudioRecorder()
transcriber = AudioTranscriber()
emotion_analyzer = EmotionAnalyzer()

# Create main window with ttkbootstrap theme
root = ttk.Window(themename="cosmo")  # You can change the theme (e.g., "cosmo", "flatly", "darkly")
root.title("Audio Recorder & Emotion Analyzer")
root.geometry("500x900")
root.configure(bg="#f0f0f0")  # Light grey background

# Bind hotkeys
root.bind("<d>", browse_directory)
root.bind("<s>", start_recording)
root.bind("<x>", stop_recording)
root.bind("<t>", transcribe_audio)
root.bind("<r>", rename_audio_file)
root.bind("<y>", rename_transcription_file)
root.bind("<e>", analyze_emotions)

# Create log box
log_box = tk.Text(root, height=10, width=60, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 10), bg="#ffffff", fg="#333333")
log_box.pack(pady=10)

# Configure logging to display in the log box
log_handler = TextBoxLogHandler(log_box)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.DEBUG)

# Browse Directory Button
browse_button = ttk.Button(
    root, text="Browse Directory (D)", command=browse_directory, bootstyle=SUCCESS, width=20
)
browse_button.pack(pady=10)

# Start Recording Button
start_button = ttk.Button(
    root, text="Start Recording (S)", command=start_recording, bootstyle=SUCCESS, width=20
)
start_button.pack(pady=10)

# Stop Recording Button
stop_button = ttk.Button(
    root, text="Stop Recording (X)", command=stop_recording, bootstyle=DANGER, state=DISABLED, width=20
)
stop_button.pack(pady=10)

# Rename Audio Button
rename_audio_button = ttk.Button(
    root, text="Rename Audio (R)", command=rename_audio_file, bootstyle=INFO, state=DISABLED, width=20
)
rename_audio_button.pack(pady=5)

# Rename Transcription Button
rename_transcription_button = ttk.Button(
    root, text="Rename Transcription (Y)", command=rename_transcription_file, bootstyle=INFO, state=DISABLED, width=20
)
rename_transcription_button.pack(pady=5)

# Transcribe Button
transcribe_button = ttk.Button(
    root, text="Transcribe (T)", command=transcribe_audio, bootstyle=INFO, state=DISABLED, width=20
)
transcribe_button.pack(pady=5)

# Analyze Emotions Button
analyze_button = ttk.Button(
    root, text="Analyze Emotions (E)", command=analyze_emotions, bootstyle=INFO, state=DISABLED, width=20
)
analyze_button.pack(pady=10)

# Transcription Box
transcription_box = tk.Text(root, height=15, width=50, wrap=tk.WORD, bg="#ffffff", fg="#333333", font=("Helvetica", 10))
transcription_box.pack(pady=10)

# Hotkey Frame
hotkey_frame = ttk.Frame(root)
hotkey_frame.pack(pady=10)

# Hotkey Label
hotkey_label = ttk.Label(
    hotkey_frame,
    text="Hotkeys:",
    font=("Helvetica", 12, "bold"),
    bootstyle=PRIMARY,
)
hotkey_label.pack()

# Hotkey List
hotkeys = [
    "D - Select Directory",
    "S - Start Recording",
    "X - Stop Recording",
    "T - Transcribe",
    "R - Rename Audio",
    "Y - Rename Transcription",
    "E - Analyze Emotions",
]

for hotkey in hotkeys:
    ttk.Label(
        hotkey_frame,
        text=hotkey,
        font=("Helvetica", 10),
        bootstyle=SECONDARY,
    ).pack(anchor="w", pady=2)

# Run the application
root.mainloop()
