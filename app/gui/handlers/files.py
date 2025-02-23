import logging
from tkinter import filedialog, simpledialog
import tkinter as tk
import os
from tkinter import messagebox
def browse_directory(Files,event=None):
    directory = filedialog.askdirectory(title="Select Directory")
    if directory:
        Files['save_directory'] = directory
        logging.info(f"Save directory selected: {Files['save_directory']}")
    else:
        logging.info(f"No directory selected. Using default: {Files['save_directory']}")

def rename_transcription_file(Files,event=None):
    if not Files['transcriber'].transcription_file:
        logging.warning("No transcription file available to rename.")
        return
    
    new_name = simpledialog.askstring("Rename Transcription File", "Enter new filename (without extension):")
    if new_name:
        if Files['transcriber'].rename_transcription(new_name):
            logging.info(f"Transcription file renamed successfully to {new_name}_transcription.txt")
        else:
            logging.error("Failed to rename transcription file")

    Files['analyze_button'].config(state=tk.NORMAL)  # Enable emotion analysis after transcription
    logging.info("Transcription displayed in the UI.")

def browse_multiple_files(Files):
    """Allow users to select multiple audio files for batch processing."""
    filepaths = filedialog.askopenfilenames(
        title="Select Audio Files", 
        filetypes=[("Audio Files", "*.wav;*.mp3;*.m4a;*.flac")]
    )
    if filepaths:
        process_batch_transcription(Files,filepaths)

def process_batch_transcription(Files,filepaths):
    """Processes multiple audio files and appends transcriptions to batch_transcription.txt."""
    batch_file = os.path.join(Files['save_directory'], "batch_transcription.txt")
    try:
        with open(batch_file, "a", encoding="utf-8") as f:
            for filepath in filepaths:
                base_name = os.path.basename(filepath)
                Files['transcription_box'].insert(tk.END, f"Processing {base_name}...\n")
                Files['root'].update()
                transcription = Files['transcriber'].transcribe_audio(filepath, Files['save_directory'])
                if transcription.startswith("Error:"):
                    Files['transcription_box'].insert(tk.END, f"Skipped {base_name} (Error)\n")
                    continue
                
                # Write a clear separator and the transcription for this file
                f.write(f"---- Transcription: {base_name} ----\n")
                f.write(transcription + "\n\n")
                Files['transcription_box'].insert(tk.END, f"Processed {base_name}\n")
        Files['transcription_box'].insert(tk.END, f"\nBatch transcription saved to: {batch_file}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Batch transcription failed: {e}")