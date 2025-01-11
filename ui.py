import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox 
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip  
from recorder import AudioRecorder
from transcriber import AudioTranscriber 
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize recorder and transcriber
recorder = AudioRecorder()
transcriber = AudioTranscriber()

# Custom font
CUSTOM_FONT = ("Segoe UI", 12)

def start_recording():
    try:
        recorder.start_recording()
        start_button.config(state=DISABLED)
        stop_button.config(state=NORMAL)
        transcribe_button.config(state=DISABLED)
        status_label.config(text="Recording in progress...", bootstyle=INFO)
        progress_bar.start()  # Start infinite progress bar animation
        logging.info("Start recording button clicked")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start recording: {str(e)}")

def stop_recording():
    try:
        recorder.stop_recording()
        start_button.config(state=NORMAL)
        stop_button.config(state=DISABLED)
        transcribe_button.config(state=NORMAL)
        status_label.config(text="Recording stopped", bootstyle=DANGER)
        progress_bar.stop()  # Stop progress bar animation
        logging.info("Stop recording button clicked")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")

def transcribe_audio():
    try:
        transcription = transcriber.transcribe_audio(recorder.filepath)
        messagebox.showinfo("Transcription Completed", f"Transcription:\n\n{transcription}")
        status_label.config(text="Transcription completed", bootstyle=SUCCESS)
        logging.info("Transcribe button clicked")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to transcribe audio: {str(e)}")


root = ttk.Window(themename="darkly")  
root.title("Audio Recorder")
root.geometry("400x400")  
root.configure(bg="#FFEBCD") 

# Start Recording Button
start_button = ttk.Button(
    root,
    text="🎤 Start Recording",
    command=start_recording,
    bootstyle=SUCCESS,
    width=20,
)
start_button.pack(pady=20)

# Stop Recording Button
stop_button = ttk.Button(
    root,
    text="⏹ Stop Recording",
    command=stop_recording,
    bootstyle=DANGER,
    state=DISABLED,
    width=20,
)
stop_button.pack(pady=20)

# Transcribe Button
transcribe_button = ttk.Button(
    root,
    text="📝 Transcribe",
    command=transcribe_audio,
    bootstyle=INFO,
    state=DISABLED,
    width=20,
)
transcribe_button.pack(pady=20)

# Infinite Progress Bar
progress_bar = ttk.Progressbar(
    root,
    orient=HORIZONTAL,
    length=300,
    mode="indeterminate",
    bootstyle=STRIPED,
)
progress_bar.pack(pady=10)

# Status Label
status_label = ttk.Label(root, text="Ready", font=CUSTOM_FONT, bootstyle=SECONDARY)
status_label.pack(pady=10)

# Tooltips
ToolTip(start_button, text="Click to start recording audio", bootstyle=(INFO, INVERSE))
ToolTip(stop_button, text="Click to stop recording audio", bootstyle=(INFO, INVERSE))
ToolTip(transcribe_button, text="Click to transcribe the recorded audio", bootstyle=(INFO, INVERSE))


root.mainloop()
