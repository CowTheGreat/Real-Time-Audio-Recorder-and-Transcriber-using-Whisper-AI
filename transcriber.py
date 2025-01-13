import os
import whisper
import logging
import shutil
import librosa
import numpy as np

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class AudioTranscriber:
    def __init__(self):
        try:
            self.model = whisper.load_model("small")
            logging.info("Whisper model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading Whisper model: {e}")
            self.model = None
        self.transcription_file = None

    def transcribe_audio(self, filepath, save_directory=None):
        if not self.model:
            logging.error("Whisper model is not loaded.")
            return "Error: Whisper model not loaded.\n"

        try:
            if not os.path.exists(filepath):
                error_msg = f"Audio file not found at: {filepath}"
                logging.error(error_msg)
                return f"Error: {error_msg}\n"

            # Load and preprocess audio file using librosa
            logging.info(f"Loading audio file: {filepath}")
            audio_data, sr = librosa.load(filepath, sr=16000, mono=True)
            
            # Ensure audio data is float32
            audio_data = audio_data.astype(np.float32)
            logging.info(f"Audio loaded successfully. Shape: {audio_data.shape}, dtype: {audio_data.dtype}")

            # Transcribe the audio data
            logging.info("Starting transcription...")
            result = self.model.transcribe(audio_data, language='en')
            transcription_text = result['text'].strip()
            logging.info("Transcription completed")
            
            if not transcription_text:  # Check if transcription is empty
                return "Error: No speech detected in the audio file.\n"

            # Save to history.txt
            self.append_to_history(transcription_text)
                
            return transcription_text
        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}\n"

    def append_to_history(self, transcription):
        """Appends the given transcription to history.txt"""
        try:
            history_file = "history.txt"

            with open(history_file, "a", encoding="utf-8") as file:
                file.write(transcription + "\n")

            logging.info("Transcription appended to history.txt")

        except Exception as e:
            logging.error(f"Error appending transcription to history.txt: {e}")

    def save_transcription(self, text, save_directory=None):
        try:
            if save_directory:
                self.transcription_file = os.path.join(save_directory, "output_transcription.txt")
            else:
                self.transcription_file = "output_transcription.txt"

            with open(self.transcription_file, "w", encoding="utf-8") as f:
                f.write(text)
            logging.info(f"Transcription saved to {self.transcription_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving transcription: {e}")
            return False

    def rename_transcription(self, new_name):
        if not self.transcription_file or not os.path.exists(self.transcription_file):
            logging.error("No transcription file exists to rename")
            return False
        
        directory = os.path.dirname(self.transcription_file)
        new_filepath = os.path.join(directory, f"{new_name}_transcription.txt")
        
        try:
            shutil.move(self.transcription_file, new_filepath)
            self.transcription_file = new_filepath
            logging.info(f"Transcription file renamed to {new_filepath}")
            return True
        except Exception as e:
            error_msg = f"Error renaming transcription file: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}\n"
