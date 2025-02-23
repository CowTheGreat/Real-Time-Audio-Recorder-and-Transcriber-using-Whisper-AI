import os
import whisper
import logging
import shutil
import librosa
import numpy as np
from ..utils.helpers import format_time

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
        self.segments_with_confidence = []

    def transcribe_audio(self, filepath, save_directory=None):
        """
        Processes a single audio file and returns a combined transcription string.
        This method maintains the existing features (confidence calculation, history update, file saving)
        and is used by the batch processing UI code to process multiple files one by one.
        """
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
            audio_data = audio_data.astype(np.float32)
            logging.info(f"Audio loaded successfully. Shape: {audio_data.shape}, dtype: {audio_data.dtype}")

            # Transcribe with word timestamps
            logging.info("Starting transcription...")
            result = self.model.transcribe(audio_data, language='en', word_timestamps=True)

            # Process segments from the transcription result
            segments = result.get('segments', [])
            if not segments:
                return "Error: No speech detected in the audio file.\n"

            # Prepare outputs: raw text and confidence details
            text_output = []
            confidence_output = []
            self.segments_with_confidence = []

            for segment in segments:
                # Extract and store text
                text = segment['text'].strip()
                text_output.append(text)

                # Format timestamp and calculate confidence
                timestamp = f"[{self._format_time(segment['start'])} - {self._format_time(segment['end'])}]"
                confidence = self._calculate_segment_confidence(segment)
                confidence_str = f"({confidence:.1%} confidence)"

                # Save segment details for potential further use
                self.segments_with_confidence.append({
                    'timestamp': timestamp,
                    'confidence': confidence_str,
                    'text': text
                })

                confidence_output.extend([timestamp, confidence_str, ""])

            # Combine outputs into strings
            text_content = " ".join(text_output)
            confidence_content = "\n".join(confidence_output)

            # Save transcription and confidence details to files
            if save_directory:
                text_file = os.path.join(save_directory, "output_transcription.txt")
                conf_file = os.path.join(save_directory, "output_transcription_confidence.txt")
            else:
                text_file = "output_transcription.txt"
                conf_file = "output_transcription_confidence.txt"

            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            with open(conf_file, 'w', encoding='utf-8') as f:
                f.write(confidence_content)

            # Update history with the transcription text
            self.update_transcription_history(text_content)

            # Return the combined transcription and confidence information for display
            return f"{text_content}\n\n{confidence_content}"

        except Exception as e:
            error_msg = f"Error during transcription: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}\n"

    def _calculate_segment_confidence(self, segment):
        """Calculate confidence score for a segment based on word-level probabilities."""
        if 'words' in segment and segment['words']:
            word_probs = []
            for word in segment['words']:
                # Handle both possible formats of word confidence
                prob = word.get('probability', word.get('confidence', 0.0))
                word_probs.append(prob)
            return sum(word_probs) / len(word_probs) if word_probs else 0.75
        return 0.75  # Default confidence if no word-level data available

    def _format_time(self, seconds):
        format_time(seconds)

    def update_transcription_history(self, text):
        """Appends the transcription to a history file."""
        history_file = "history.txt"
        try:
            with open(history_file, "a", encoding="utf-8") as f:
                f.write(text + "\n")
            logging.info(f"Transcription appended to {history_file}")
        except Exception as e:
            logging.error(f"Error updating transcription history: {e}")

    def save_transcription(self, text, save_directory=None):
        """This method is maintained for compatibility but file saving is handled in transcribe_audio"""
        self.transcription_file = os.path.join(save_directory, "output_transcription.txt") if save_directory else "output_transcription.txt"
        return True

    def rename_transcription(self, new_name):
        if not self.transcription_file or not os.path.exists(self.transcription_file):
            logging.error("No transcription file exists to rename")
            return False
        
        directory = os.path.dirname(self.transcription_file)
        new_filepath = os.path.join(directory, f"{new_name}_transcription.txt")
        new_confidence_filepath = os.path.join(directory, f"{new_name}_confidence.txt")
        
        try:
            # Move the main transcription file
            shutil.move(self.transcription_file, new_filepath)
            self.transcription_file = new_filepath
            
            # Move the confidence file if it exists
            old_confidence_file = os.path.join(directory, "output_transcription_confidence.txt")
            if os.path.exists(old_confidence_file):
                shutil.move(old_confidence_file, new_confidence_filepath)
                
            logging.info(f"Transcription files renamed to {new_filepath}")
            return True
        except Exception as e:
            error_msg = f"Error renaming transcription file: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}\n"
