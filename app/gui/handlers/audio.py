import logging
import tkinter as tk
from tkinter import simpledialog
def start_recording(Recording,event=None):
    if not Recording['save_directory']:
        logging.warning("Save directory is not set. Please select a directory first.")
        return
    
    Recording['recorder'].set_save_directory(Recording['save_directory'])
    try:
        Recording['recorder'].start_recording()
        Recording['visualizer'].start_recording()
        Recording['start_button'].config(state=tk.DISABLED)
        Recording['stop_button'].config(state=tk.NORMAL)
        Recording['transcribe_button'].config(state=tk.DISABLED)
        Recording['rename_audio_button'].config(state=tk.DISABLED)
        Recording['rename_transcription_button'].config(state=tk.DISABLED)
        Recording['analyze_button'].config(state=tk.DISABLED)  # Disable emotion analysis button

        # threading.Thread(target = plot_waveform).start()

        Recording['transcription_box'].delete(1.0, tk.END)  # Clear previous transcription
        logging.info("Start recording button clicked")
    except RuntimeError as e:
        logging.error(e)
        Recording['log_box'].config(state=tk.NORMAL)
        Recording['log_box'].insert(tk.END, f"Error: {e}\n")
        Recording['log_box'].config(state=tk.DISABLED)

def stop_recording(Recording,event=None):
    Recording['recorder'].stop_recording()
    Recording['visualizer'].stop_recording()
    Recording['start_button'].config(state=tk.NORMAL)
    Recording['stop_button'].config(state=tk.DISABLED)
    Recording['transcribe_button'].config(state=tk.NORMAL)
    Recording['rename_audio_button'].config(state=tk.NORMAL)
    logging.info("Stop recording button clicked")

def transcribe_audio(Recording,event=None):
    filepath=Recording['recorder'].filepath
    if not Recording['recorder'].filepath:
        logging.warning("No audio file available for transcription.")
        Recording['transcription_box'].insert(tk.END, "No audio file available for transcription.\n")
        return
    
    try:
        # Clear previous transcription
        Recording['transcription_box'].delete(1.0, tk.END)
        Recording['transcription_box'].insert(tk.END, "Transcribing audio...\n")
        Recording['root'].update()
        
        # Get transcription with confidence scores
        transcription = Recording['transcriber'].transcribe_audio(Recording['recorder'].filepath, Recording['save_directory'])
        Recording['analyze_button'].config(state=tk.NORMAL)  # Enable emotion analysis after transcription

        # Check for errors and handle transcription
        if not transcription.startswith("Error:"):
            # Save transcription to file
            if Recording['transcriber'].save_transcription(transcription, Recording['save_directory']):
                # Enable rename button only if save was successful
                Recording['rename_transcription_button'].config(state=tk.NORMAL)
            
            # Format and display transcription in text box with colors
            Recording['transcription_box'].delete(1.0, tk.END)
            
            # Split transcription into lines
            lines = transcription.split('\n')
            
            # Configure text tags for different confidence levels
            Recording['transcription_box'].tag_configure("high_conf", foreground="#4CAF50")  # Green
            Recording['transcription_box'].tag_configure("med_conf", foreground="#FFA726")   # Orange
            Recording['transcription_box'].tag_configure("low_conf", foreground="#F44336")   # Red
            Recording['transcription_box'].tag_configure("header", font=("Helvetica", 12, "bold"))
            Recording['transcription_box'].tag_configure("separator", foreground="#666666")
            
            # Process and display each line with appropriate formatting
            for line in lines:
                if "TRANSCRIPTION WITH CONFIDENCE SCORES" in line:
                    Recording['transcription_box'].insert(tk.END, line + '\n', "header")
                elif line.startswith('=') or line.startswith('-'):
                    Recording['transcription_box'].insert(tk.END, line + '\n', "separator")
                elif '(' in line and ')' and 'confidence' in line:
                    # Extract confidence percentage
                    conf_start = line.find('(') + 1
                    conf_end = line.find('%')
                    if conf_start > 0 and conf_end > 0:
                        try:
                            confidence = float(line[conf_start:conf_end])
                            if confidence >= 90:
                                Recording['transcription_box'].insert(tk.END, line + '\n', "high_conf")
                            elif confidence >= 70:
                                Recording['transcription_box'].insert(tk.END, line + '\n', "med_conf")
                            else:
                                Recording['transcription_box'].insert(tk.END, line + '\n', "low_conf")
                        except ValueError:
                            Recording['transcription_box'].insert(tk.END, line + '\n')
                    else:
                        Recording['transcription_box'].insert(tk.END, line + '\n')
                else:
                    Recording['transcription_box'].insert(tk.END, line + '\n')
            
            # Calculate word count
            word_count = len(transcription.split())

            # Calculate words per second
            recording_duration = Recording['recorder'].recording_duration  # Access directly
            words_per_second = word_count / recording_duration if recording_duration > 0 else 0

            # Display words per second and confidence score
            Recording['transcription_box'].insert(tk.END, f"\nWords per second: {words_per_second:.2f}\n")
                    
            logging.info("Transcription with confidence scores displayed in the UI.")
        else:
            # If there was an error, display it and disable rename button
            Recording['transcription_box'].delete(1.0, tk.END)
            Recording['transcription_box'].insert(tk.END, transcription)
            Recording['rename_transcription_button'].config(state=tk.DISABLED)
            logging.error("Failed to transcribe audio")
            
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        Recording['transcription_box'].delete(1.0, tk.END)
        Recording['transcription_box'].insert(tk.END, f"Error during transcription: {str(e)}")
        Recording['rename_transcription_button'].config(state=tk.DISABLED)

def rename_audio_file(Recording,event=None):
    if not Recording['recorder'].filepath:
        logging.warning("No audio file available to rename.")
        return
    
    new_name = simpledialog.askstring("Rename Audio File", "Enter new filename (without extension):")
    if new_name:
        if Recording['recorder'].rename_audio(new_name):
            logging.info(f"Audio file renamed successfully to {new_name}.wav")
        else:
            logging.error("Failed to rename audio file")