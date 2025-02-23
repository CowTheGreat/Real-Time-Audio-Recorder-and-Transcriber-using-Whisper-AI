import warnings
from app.core.recorder import AudioRecorder
from app.gui.components.waveform import WaveformVisualizer
from app.gui.components.log_handler import TextBoxLogHandler
recorder = AudioRecorder()

# Suppress specific warning
warnings.filterwarnings(
    "ignore",
    message=(
        "You are using `torch.load` with `weights_only=False`.*"
    ),
)

import tkinter as tk
from app.core.recorder import AudioRecorder
from app.core.transcriber import AudioTranscriber
from app.core.emotion_analyzer import EmotionAnalyzer
from app.core.text_processor import TextProcessor
from app.core.text_analyzer import TextAnalyzer
from app.gui.handlers.export import export_transcription
from app.gui.handlers.audio import start_recording, stop_recording, transcribe_audio, rename_audio_file
from app.utils.config import get_styles
from app.gui.handlers.analysis import analyze_emotions, analyze_text_content, set_api_key, summarize_text, query_text
from app.gui.handlers.theme import toggle_theme
from app.gui.handlers.files import browse_directory, rename_transcription_file, browse_multiple_files
from app.gui.layout.dashboard import open_new_dashboard
from app.gui.layout.window import open_annotation_window
from app.gui.components.setup import setup_tkdnd
import logging
import warnings
import os
from tkinterdnd2 import TkinterDnD
import matplotlib
matplotlib.use("TkAgg")
# Suppress FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

styles=get_styles()
current_theme = styles['dark_theme']

# Set default save directory to the current working directory
save_directory = os.getcwd()
logging.info(f"Default save directory set to: {save_directory}")
root = TkinterDnD.Tk()
# Create a new horizontal frame
main_frame = tk.Frame(root, bg="#2b2b2b")
main_frame.pack(fill=tk.X, padx=10, pady=5)
button_container = tk.Frame(root, bg="#2b2b2b")
button_container.pack(in_=main_frame, side=tk.LEFT, fill=tk.Y)
# Create log box
log_box = tk.Text(button_container, height=8, width=60, wrap=tk.WORD, state=tk.DISABLED, bg="#333333", fg="white", font=("Helvetica", 10))
log_box.pack(pady=5)
rename_transcription_button = tk.Button(
    button_container,
    text="Rename Transcription (Y)",
    command=lambda:rename_transcription_file(Files),
    state=tk.DISABLED,
    **styles['button_style']
)
rename_transcription_button.pack(pady=3)
# Create a frame for transcription
transcription_frame = tk.Frame(root, bg="#2b2b2b")
transcription_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
control_frame = tk.Frame(transcription_frame, bg="#2b2b2b")
control_frame.pack(fill=tk.X, pady=5)
# Create a frame for the text box and scrollbar
text_container = tk.Frame(transcription_frame, bg="#2b2b2b")
text_container.pack(fill=tk.BOTH, expand=True)
# Add scrollbar
scrollbar = tk.Scrollbar(text_container)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
transcribe_button = tk.Button(
    button_container, text="Transcribe (T)", command=lambda:transcribe_audio(Recording), state=tk.DISABLED, **styles['button_style']
)
analyze_button = tk.Button(
    button_container, text="Analyze Emotions (E)", command=lambda:analyze_emotions(Analysis), state=tk.DISABLED, **styles['button_style']
)
analyze_button.pack(pady=3)
transcribe_button.pack(pady=3)
# Transcription Box
transcription_box = tk.Text(
    text_container,
    height=12,
    width=50,
    wrap=tk.WORD,
    bg="#333333",
    fg="white",
    font=("Helvetica", 11),
    yscrollcommand=scrollbar.set
)
transcription_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
recorder = AudioRecorder()
transcriber = AudioTranscriber()
emotion_analyzer = EmotionAnalyzer()
text_processor = TextProcessor()  # Will automatically load API key from .env if available
waveform_frame = tk.Frame(root, bg="#2b2b2b")
waveform_frame.pack(in_=main_frame, side=tk.RIGHT, padx=5)
visualizer = WaveformVisualizer(waveform_frame)
text_analyzer = TextAnalyzer()
start_button = tk.Button(
    button_container, text="Start Recording (S)", command=lambda:start_recording(Recording), **styles['button_style']
)
start_button.pack(pady=3)

stop_button = tk.Button(
    button_container,
    text="Stop Recording (X)",
    command=lambda:stop_recording(Recording),
    state=tk.DISABLED,
    **styles['button_style']
)
stop_button.pack(pady=3)

rename_audio_button = tk.Button(
    button_container,
    text="Rename Audio (R)",
    command=lambda:rename_audio_file(Recording),
    state=tk.DISABLED,
    **styles['button_style']
)
rename_audio_button.pack(pady=3)

root.title("Audio Recorder & Emotion Analyzer")
root.geometry("1000x900")
root.configure(bg="#2b2b2b")
# root.tk.eval('package require tkdnd')
Recording={"save_directory":save_directory,"recorder":recorder,"visualizer":visualizer,"start_button":start_button,"stop_button":stop_button,"transcribe_button":transcribe_button,"rename_audio_button":rename_audio_button,"rename_transcription_button":rename_transcription_button,"analyze_button":analyze_button,"transcription_box":transcription_box,"log_box":log_box,'root':root,'transcriber':transcriber}
Analysis={'recorder':recorder,'emotion_analyzer':emotion_analyzer,'text_analyzer':text_analyzer,'text_processor':text_processor,'save_directory':save_directory,'transcription_box':transcription_box,'root':root}
Files={"transcriber":transcriber,"transcription_box":transcription_box,"analyze_button":analyze_button,"root":root,"transcription_box":transcription_box,"save_directory":save_directory}
# Bind hotkeys
root.bind("<d>", lambda:browse_directory(Files))
root.bind("<s>", lambda:start_recording(Recording))
root.bind("<x>", lambda:stop_recording(Recording))
root.bind("<t>", lambda:transcribe_audio(Recording))

root.bind("<r>", lambda:rename_audio_file(Recording))
root.bind("<y>", lambda:rename_transcription_file(Files))
root.bind("<e>", lambda:analyze_emotions(Analysis))

# Export Transcription Button
export_button = tk.Button(
    waveform_frame,
    text="Export Transcription",
    command=lambda: export_transcription(transcriber),
    bg="#008CBA",
    fg="white",
    font=("Helvetica", 12, "bold"),
    bd=3, width=20,
    height= 1,
    relief=tk.RAISED
)
export_button.pack(pady=3)
# Transcription Label
transcription_label = tk.Label(
    transcription_frame,
    text="Transcription and Analysis",
    bg="#2b2b2b",
    fg="white",
    font=("Helvetica", 12, "bold")
)
transcription_label.pack(pady=5)
# Add hotkey label at the bottom
hotkey_label = tk.Label(
    root,
    text="Hotkeys:\nD - Select Directory | S - Start Recording | X - Stop Recording\nT - Transcribe | R - Rename Audio | Y - Rename Transcription | E - Analyze Emotions",
    bg="#2b2b2b",
    fg="white",
    font=("Helvetica", 10),
)
hotkey_label.pack(pady=5)
# Configure logging to display in the log box
log_handler = TextBoxLogHandler(log_box)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.DEBUG)
Theme={"root":root,"main_frame":main_frame,"button_container":button_container,"waveform_frame":waveform_frame,"transcription_frame":transcription_frame,"text_container":text_container,"log_box":log_box,"transcription_box":transcription_box,"transcription_label":transcription_label,"hotkey_label":hotkey_label,"control_frame":control_frame,"visualizer":visualizer,'current_theme':current_theme}
theme_button = tk.Button(
    button_container, 
    text="Toggle Theme", 
    command=lambda:toggle_theme(Theme), 
    **styles['button_style']
)
theme_button.pack(pady=3)
browse_button = tk.Button(
    button_container, text="Browse Directory (D)", command=lambda:browse_directory(Files), **styles['button_style']
)
browse_button.pack(pady=3)

# Batch Transcription Button
batch_button = tk.Button(
    button_container, 
    text="Batch Transcription", 
    command=lambda:browse_multiple_files(Files), 
    bg="#FFA500", bd=3, relief=tk.RAISED, width=20,
    height= 1, font=("Helvetica", 12, "bold"), fg="white"
    
)
batch_button.pack(pady=3)

#Usage Dashboard Button
dashboard_button = tk.Button(button_container, text="Usage Dashboard", command=lambda:open_new_dashboard(save_directory,root), **styles['button_style'])
dashboard_button.pack(pady=3)

analyze_text_button = tk.Button(button_container, text="Analyze Text", command=lambda:analyze_text_content(Analysis))
analyze_text_button.pack(side=tk.LEFT, padx=5)

api_key_button = tk.Button(button_container, text="Set API Key", command=lambda:set_api_key(Analysis))
api_key_button.pack(side=tk.LEFT, padx=5)

summarize_button = tk.Button(button_container, text="Summarize", command=lambda:summarize_text(Analysis))
summarize_button.pack(side=tk.LEFT, padx=5)

query_button = tk.Button(button_container, text="Ask Question", command=lambda:query_text(Analysis))
query_button.pack(side=tk.LEFT, padx=5)
Window={"root":root,"save_directory":save_directory,"transcription_box":transcription_box,"control_frame":control_frame}
# Annotate Transcription Button
annotate_button = tk.Button(button_container, text="Annotate Transcription", command=lambda:open_annotation_window(Window), bg="#4caf50", fg="white", font=("Helvetica", 9, "bold"), bd=3, relief=tk.RAISED)
annotate_button.pack(pady=3)

scrollbar.config(command=transcription_box.yview)

setup_tkdnd(root)

root.mainloop()