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
from tkinter import filedialog, TclError, messagebox
from recorder import AudioRecorder
from transcriber import AudioTranscriber
from emotion_analyzer import EmotionAnalyzer
from text_processor import TextProcessor
from text_analyzer import TextAnalyzer
import logging
import warnings
import os
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pyaudio
import hashlib
# Suppress FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

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
class DropZone(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(relief="groove", borderwidth=2)
        
        # Enable drag and drop for files
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
        
    def handle_drop(self, event):
        # Get the dropped file path and handle it
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        handle_dropped_file(file_path)

def handle_dropped_file(file_path):
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        logging.error(error_msg)
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, f"Error: {error_msg}")
        return
        
    # Check if it's an audio file
    valid_extensions = ('.wav', '.mp3', '.m4a', '.flac')
    if not file_path.lower().endswith(valid_extensions):
        error_msg = "Invalid file type. Please drop an audio file."
        logging.error(error_msg)
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, f"Error: {error_msg}")
        return
        
    try:
        # Update the UI to show file is being processed
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, "Processing dropped file...\n")
        root.update()
        
        # Set the filepath in the recorder
        recorder.filepath = file_path
        
        # Enable relevant buttons
        transcribe_button.config(state=tk.NORMAL)
        rename_audio_button.config(state=tk.NORMAL)
        
        # Automatically start transcription
        transcribe_audio()
        
    except Exception as e:
        error_msg = f"Error processing dropped file: {str(e)}"
        logging.error(error_msg)
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, f"Error: {error_msg}")

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
        visualizer.start_recording()
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        transcribe_button.config(state=tk.DISABLED)
        rename_audio_button.config(state=tk.DISABLED)
        rename_transcription_button.config(state=tk.DISABLED)
        analyze_button.config(state=tk.DISABLED)  # Disable emotion analysis button

        # threading.Thread(target = plot_waveform).start()

        transcription_box.delete(1.0, tk.END)  # Clear previous transcription
        logging.info("Start recording button clicked")
    except RuntimeError as e:
        logging.error(e)
        log_box.config(state=tk.NORMAL)
        log_box.insert(tk.END, f"Error: {e}\n")
        log_box.config(state=tk.DISABLED)

def stop_recording(event=None):
    recorder.stop_recording()
    visualizer.stop_recording()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    transcribe_button.config(state=tk.NORMAL)
    rename_audio_button.config(state=tk.NORMAL)
    logging.info("Stop recording button clicked")

def transcribe_audio(event=None):
    if not recorder.filepath:
        logging.warning("No audio file available for transcription.")
        transcription_box.insert(tk.END, "No audio file available for transcription.\n")
        return
    
    try:
        # Clear previous transcription
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, "Transcribing audio...\n")
        root.update()
        
        # Get transcription with confidence scores
        transcription = transcriber.transcribe_audio(recorder.filepath, save_directory)
        analyze_button.config(state=tk.NORMAL)  # Enable emotion analysis after transcription

        # Check for errors and handle transcription
        if not transcription.startswith("Error:"):
            # Save transcription to file
            if transcriber.save_transcription(transcription, save_directory):
                # Enable rename button only if save was successful
                rename_transcription_button.config(state=tk.NORMAL)
            
            # Format and display transcription in text box with colors
            transcription_box.delete(1.0, tk.END)
            
            # Split transcription into lines
            lines = transcription.split('\n')
            
            # Configure text tags for different confidence levels
            transcription_box.tag_configure("high_conf", foreground="#4CAF50")  # Green
            transcription_box.tag_configure("med_conf", foreground="#FFA726")   # Orange
            transcription_box.tag_configure("low_conf", foreground="#F44336")   # Red
            transcription_box.tag_configure("header", font=("Helvetica", 12, "bold"))
            transcription_box.tag_configure("separator", foreground="#666666")
            
            # Process and display each line with appropriate formatting
            for line in lines:
                if "TRANSCRIPTION WITH CONFIDENCE SCORES" in line:
                    transcription_box.insert(tk.END, line + '\n', "header")
                elif line.startswith('=') or line.startswith('-'):
                    transcription_box.insert(tk.END, line + '\n', "separator")
                elif '(' in line and ')' and 'confidence' in line:
                    # Extract confidence percentage
                    conf_start = line.find('(') + 1
                    conf_end = line.find('%')
                    if conf_start > 0 and conf_end > 0:
                        try:
                            confidence = float(line[conf_start:conf_end])
                            if confidence >= 90:
                                transcription_box.insert(tk.END, line + '\n', "high_conf")
                            elif confidence >= 70:
                                transcription_box.insert(tk.END, line + '\n', "med_conf")
                            else:
                                transcription_box.insert(tk.END, line + '\n', "low_conf")
                        except ValueError:
                            transcription_box.insert(tk.END, line + '\n')
                    else:
                        transcription_box.insert(tk.END, line + '\n')
                else:
                    transcription_box.insert(tk.END, line + '\n')
            
            logging.info("Transcription with confidence scores displayed in the UI.")
        else:
            # If there was an error, display it and disable rename button
            transcription_box.delete(1.0, tk.END)
            transcription_box.insert(tk.END, transcription)
            rename_transcription_button.config(state=tk.DISABLED)
            logging.error("Failed to transcribe audio")
            
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        transcription_box.delete(1.0, tk.END)
        transcription_box.insert(tk.END, f"Error during transcription: {str(e)}")
        rename_transcription_button.config(state=tk.DISABLED)

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

    analyze_button.config(state=tk.NORMAL)  # Enable emotion analysis after transcription
    logging.info("Transcription displayed in the UI.")


def analyze_emotions(event=None):
    if not recorder.filepath or not os.path.exists(recorder.filepath):
        logging.warning("No audio file available for emotion analysis.")
        transcription_box.insert(tk.END, "\nNo audio file available for emotion analysis.")
        return
    
    try:
        # Get the current transcription text (excluding confidence scores and formatting)
        current_text = transcription_box.get("1.0", tk.END).strip()
        
        # Extract just the transcribed text, removing confidence scores and formatting
        clean_text = ""
        for line in current_text.split('\n'):
            if not any(x in line for x in ['confidence', '===', '---', 'TRANSCRIPTION']):
                if not line.startswith('[') and not line.strip() == "":
                    clean_text += line.strip() + " "
        
        if not clean_text:
            logging.warning("No transcription available for emotion analysis.")
            return
            
        # Perform emotion analysis
        emotion_analysis = emotion_analyzer.analyze(clean_text, recorder.filepath)
        
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
        
def analyze_text_content(event=None):
    """Analyze the transcribed text for key topics and entities."""    
    try:
        # Get the path to the transcription file
        transcription_file = os.path.join(save_directory, "output_transcription.txt") if save_directory else "output_transcription.txt"
        
        if not os.path.exists(transcription_file):
            logging.warning("No transcription file found.")
            return
            
        # Read the transcription file
        with open(transcription_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # Extract just the transcribed text, removing timestamps, confidence scores and formatting
        clean_text = ""
        for line in content.split('\n'):
            # Skip lines with metadata and formatting
            if (not any(x in line.lower() for x in ['confidence', '=', '-', 'transcription']) and 
                not line.strip().startswith('[') and 
                line.strip()):
                clean_text += line.strip() + " "
                
        if not clean_text:
            logging.error("No text to analyze")
            return
            
        # Perform analysis
        analysis_results = text_analyzer.analyze_text(clean_text)
        formatted_results = text_analyzer.format_analysis_results(analysis_results)
        
        # Show results in a new window
        analysis_window = tk.Toplevel(root)
        analysis_window.title("Text Analysis")
        analysis_window.geometry("600x600")
        
        # Create text widget with scrollbar
        analysis_text = tk.Text(analysis_window, wrap=tk.WORD, height=30, width=70)
        scrollbar = tk.Scrollbar(analysis_window, command=analysis_text.yview)
        analysis_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
        
        # Insert analysis results
        analysis_text.insert("1.0", formatted_results)
        analysis_text.config(state=tk.DISABLED)
        
        # Save analysis results to file
        analysis_path = os.path.join(save_directory, "text_analysis.txt") if save_directory else "text_analysis.txt"
        with open(analysis_path, "w", encoding="utf-8") as f:
            f.write(formatted_results)
        logging.info(f"Text analysis saved to {analysis_path}")
        
    except Exception as e:
        logging.error(f"Error during text analysis: {e}")

def set_api_key(event=None):
    api_key = simpledialog.askstring("API Key", "Enter your Gemini API Key:", show='*')
    if api_key:
        success = text_processor.set_api_key(api_key)
        if success:
            logging.info("API key set successfully")
        else:
            logging.error("Failed to initialize with provided API key")

def summarize_text(event=None):
    if not text_processor.model:
        logging.error("Please set Gemini API key first")
        return
        
    try:
        # Get text from transcription text widget
        text = transcription_box.get("1.0", tk.END).strip()
        if not text:
            logging.error("No text to summarize")
            return
            
        summary = text_processor.summarize_text(text)
        
        # Show summary in a new window
        summary_window = tk.Toplevel(root)
        summary_window.title("Summary")
        summary_window.geometry("600x400")
        
        summary_text = tk.Text(summary_window, wrap=tk.WORD, height=15, width=60)
        summary_text.pack(padx=10, pady=10, expand=True, fill='both')
        summary_text.insert("1.0", summary)
        summary_text.config(state=tk.DISABLED)
        
    except Exception as e:
        logging.error(f"Error generating summary: {e}")

def query_text(event=None):
    if not text_processor.model:
        logging.error("Please set Gemini API key first")
        return
        
    try:
        # Get text from transcription text widget
        text = transcription_box.get("1.0", tk.END).strip()
        if not text:
            logging.error("No text to query")
            return
            
        # Get query from user
        query = simpledialog.askstring("Query", "Enter your question about the text:")
        if not query:
            return
            
        answer = text_processor.query_text(text, query)
        
        # Show answer in a new window
        answer_window = tk.Toplevel(root)
        answer_window.title("Answer")
        answer_window.geometry("600x400")
        
        answer_text = tk.Text(answer_window, wrap=tk.WORD, height=15, width=60)
        answer_text.pack(padx=10, pady=10, expand=True, fill='both')
        answer_text.insert("1.0", answer)
        answer_text.config(state=tk.DISABLED)
        
    except Exception as e:
        logging.error(f"Error processing query: {e}")


class WaveformVisualizer:
    def __init__(self, frame):
        self.frame = frame
        self.is_recording = False
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(4, 4), dpi=100, facecolor='#2b2b2b')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        # Set up the line plot with matching dimensions
        self.chunk_size = 1024
        self.x = np.arange(0, self.chunk_size)
        self.line, = self.ax.plot(self.x, np.zeros(self.chunk_size), color='#4caf50')
        
        # Configure plot appearance
        self.ax.set_ylim(-32768, 32767)
        self.ax.set_xlim(0, self.chunk_size)
        self.ax.grid(True, color='#444444')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg='#2b2b2b', highlightthickness=0)
        self.canvas_widget.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Audio stream configuration
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.p = None
        self.stream = None

    def start_recording(self):
        self.is_recording = True
        threading.Thread(target=self._record_stream, daemon=True).start()

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

    def _record_stream(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size)
                audio_data = np.frombuffer(data, dtype=np.int16)
                self.line.set_ydata(audio_data)
                self.canvas.draw_idle()
            except Exception as e:
                print(f"Error reading audio stream: {e}")
                break

        self.stop_recording()

recorder = AudioRecorder()
transcriber = AudioTranscriber()
emotion_analyzer = EmotionAnalyzer()
text_processor = TextProcessor()  # Will automatically load API key from .env if available

text_analyzer = TextAnalyzer()
root = TkinterDnD.Tk()

def open_annotation_window():
    # Create a new top-level window for annotations
    annotation_win = tk.Toplevel(root)
    annotation_win.title("Annotate Transcription")
    annotation_win.geometry("600x400")

    # Create a frame for layout
    frame = tk.Frame(annotation_win, padx=10, pady=10, bg="#2b2b2b")
    frame.pack(fill=tk.BOTH, expand=True)

    # Label for transcription display
    transcription_label = tk.Label(frame, text="Transcription", bg="#2b2b2b", fg="white", font=("Helvetica", 12, "bold"))
    transcription_label.pack(anchor="w")

    # Read-only text widget to display the current transcription
    transcription_display = tk.Text(frame, height=10, wrap=tk.WORD)
    transcription_display.pack(fill=tk.BOTH, expand=True, pady=(0,10))
    transcription_text = transcription_box.get("1.0", tk.END).strip()
    transcription_display.insert(tk.END, transcription_text)
    transcription_display.config(state=tk.DISABLED)

    # Label for annotation input
    annotation_label = tk.Label(frame, text="Enter your comments/annotations:", bg="#2b2b2b", fg="white", font=("Helvetica", 12, "bold"))
    annotation_label.pack(anchor="w")

    # Text widget for user annotations
    annotation_text_widget = tk.Text(frame, height=5, wrap=tk.WORD)
    annotation_text_widget.pack(fill=tk.BOTH, expand=True, pady=(0,10))

    # Function to save annotated transcription
    def save_annotation():
        comments = annotation_text_widget.get("1.0", tk.END).strip()
        if not transcription_text:
            messagebox.showwarning("Warning", "No transcription available to annotate.")
            return

        # Generate a unique filename based on the transcription content
        transcription_hash = hashlib.md5(transcription_text.encode()).hexdigest()[:8]  # Short hash for uniqueness
        annotated_file = os.path.join(save_directory, f"annotated_transcription_{transcription_hash}.txt")

        # Save both the transcription and the comments
        try:
            with open(annotated_file, "a", encoding="utf-8") as f:
                if os.path.getsize(annotated_file) == 0:  # If it's a new file, add transcription
                    f.write(f"Transcription:\n{transcription_text}\n\n")
                f.write(f"User Comments:\n{comments}\n\n")  # Append new comments
                
            messagebox.showinfo("Success", f"Annotated transcription saved to {annotated_file}")
            annotation_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save annotation: {e}")


    # Save Annotation button
    save_button = tk.Button(frame, text="Save Annotation", command=save_annotation, bg="#4caf50", fg="white", font=("Helvetica", 12, "bold"), bd=3, relief=tk.RAISED)
    save_button.pack(pady=5)

root.title("Audio Recorder & Emotion Analyzer")
root.geometry("1000x900")
root.configure(bg="#2b2b2b")
# root.tk.eval('package require tkdnd')

# Bind hotkeys
root.bind("<d>", browse_directory)
root.bind("<s>", start_recording)
root.bind("<x>", stop_recording)
root.bind("<t>", transcribe_audio)

root.bind("<r>", rename_audio_file)
root.bind("<y>", rename_transcription_file)
root.bind("<e>", analyze_emotions)

# Create a new horizontal frame
main_frame = tk.Frame(root, bg="#2b2b2b")
main_frame.pack(fill=tk.X, padx=10, pady=5)

button_container = tk.Frame(root, bg="#2b2b2b")
button_container.pack(in_=main_frame, side=tk.LEFT, fill=tk.Y)

waveform_frame = tk.Frame(root, bg="#2b2b2b")
waveform_frame.pack(in_=main_frame, side=tk.RIGHT, padx=5)

visualizer = WaveformVisualizer(waveform_frame)

# Create log box
log_box = tk.Text(button_container, height=8, width=60, wrap=tk.WORD, state=tk.DISABLED, bg="#333333", fg="white", font=("Helvetica", 10))
log_box.pack(pady=5)

# Configure logging to display in the log box
log_handler = TextBoxLogHandler(log_box)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.DEBUG)
drop_zone = DropZone(
    root,
    text="Drag and drop audio files here\nor use the buttons below",
    bg="#333333",
    fg="white",
    font=("Helvetica", 12),
    width=40,
    height=3
)
drop_zone.pack(fill=tk.X, padx=10, pady=5)
root.tk.eval(f'tkdnd::drop_target register {drop_zone.winfo_pathname(drop_zone.winfo_id())} *')
root.tk.eval(f'tkdnd::drop_target register {root.winfo_pathname(root.winfo_id())} *')

button_style = {
    "font": ("Helvetica", 12, "bold"),
    "bg": "#4caf50",
    "fg": "white",
    "activebackground": "#45a049",
    "activeforeground": "white",
    "relief": tk.RAISED,
    "bd": 3,
    "width": 20,
    "height": 1, 
}

browse_button = tk.Button(
    button_container, text="Browse Directory (D)", command=browse_directory, **button_style
)
browse_button.pack(pady=3)

start_button = tk.Button(
    button_container, text="Start Recording (S)", command=start_recording, **button_style
)
start_button.pack(pady=3)

stop_button = tk.Button(
    button_container,
    text="Stop Recording (X)",
    command=stop_recording,
    state=tk.DISABLED,
    **button_style
)
stop_button.pack(pady=3)

rename_audio_button = tk.Button(
    button_container,
    text="Rename Audio (R)",
    command=rename_audio_file,
    state=tk.DISABLED,
    **button_style
)
rename_audio_button.pack(pady=3)

rename_transcription_button = tk.Button(
    button_container,
    text="Rename Transcription (Y)",
    command=rename_transcription_file,
    state=tk.DISABLED,
    **button_style
)
rename_transcription_button.pack(pady=3)

transcribe_button = tk.Button(
    button_container, text="Transcribe (T)", command=transcribe_audio, state=tk.DISABLED, **button_style
)
transcribe_button.pack(pady=3)

analyze_button = tk.Button(
    button_container, text="Analyze Emotions (E)", command=analyze_emotions, state=tk.DISABLED, **button_style
)
analyze_button.pack(pady=3)

analyze_text_button = tk.Button(button_container, text="Analyze Text", command=analyze_text_content)
analyze_text_button.pack(side=tk.LEFT, padx=5)

api_key_button = tk.Button(button_container, text="Set API Key", command=set_api_key)
api_key_button.pack(side=tk.LEFT, padx=5)

summarize_button = tk.Button(button_container, text="Summarize", command=summarize_text)
summarize_button.pack(side=tk.LEFT, padx=5)

query_button = tk.Button(button_container, text="Ask Question", command=query_text)
query_button.pack(side=tk.LEFT, padx=5)

# Annotate Transcription Button
annotate_button = tk.Button(button_container, text="Annotate Transcription", command=open_annotation_window, bg="#4caf50", fg="white", font=("Helvetica", 9, "bold"), bd=3, relief=tk.RAISED)
annotate_button.pack(pady=3)

# Create a frame for transcription
transcription_frame = tk.Frame(root, bg="#2b2b2b")
transcription_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Transcription Label
transcription_label = tk.Label(
    transcription_frame,
    text="Transcription and Analysis",
    bg="#2b2b2b",
    fg="white",
    font=("Helvetica", 12, "bold")
)
transcription_label.pack(pady=5)

# Create a frame for the text box and scrollbar
text_container = tk.Frame(transcription_frame, bg="#2b2b2b")
text_container.pack(fill=tk.BOTH, expand=True)

# Add scrollbar
scrollbar = tk.Scrollbar(text_container)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
scrollbar.config(command=transcription_box.yview)
def setup_tkdnd():
    try:
        root.tk.eval('package require tkdnd')
        root.tk.call('tkdnd::drop_target', 'register', root, ('DND_Files', 'Files'))
        logging.info("TkDND initialized successfully")
    except tk.TclError as e:
        logging.error(f"Failed to initialize TkDND: {e}")
        # Create a label to show error
        tk.Label(
            root,
            text="Drag and drop not available.\nPlease install python-tkdnd package.",
            bg="#ff6b6b",
            fg="white",
            font=("Helvetica", 10)
        ).pack(fill=tk.X, padx=10, pady=5)

setup_tkdnd()
# Add hotkey label at the bottom
hotkey_label = tk.Label(
    root,
    text="Hotkeys:\nD - Select Directory | S - Start Recording | X - Stop Recording\nT - Transcribe | R - Rename Audio | Y - Rename Transcription | E - Analyze Emotions",
    bg="#2b2b2b",
    fg="white",
    font=("Helvetica", 10),
)
hotkey_label.pack(pady=5)

root.mainloop()