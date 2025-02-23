import pyaudio
import wave
import threading
import logging
import os
import shutil
import time

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False
        self.filepath = None
        self.recording_start_time = None  
        self.recording_duration = 0 
    
    def set_save_directory(self, directory):
        self.save_directory = directory
        logging.info(f"Save directory set to: {self.save_directory}")

    def start_recording(self):
        self.frames = []
        self.recording_start_time = time.time()
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
            )
            self.recording = True
            self.thread = threading.Thread(target=self.record)
            self.thread.start()
            logging.info("Recording started")
        except Exception as e:
            logging.error(f"Error starting recording: {e}")
            raise RuntimeError(f"Error starting recording: {e}")

    def record(self):
        while self.recording:
            data = self.stream.read(1024)
            self.frames.append(data)

    def stop_recording(self):
        self.recording = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.recording_duration = time.time() - self.recording_start_time
        self.save_recording()
        logging.info("Recording stopped and saved")

    def save_recording(self):
        # Always save as output.wav in the specified directory
        if hasattr(self, "save_directory"):
            self.filepath = os.path.join(self.save_directory, "output.wav")
        else:
            self.filepath = "output.wav"

        wf = wave.open(self.filepath, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b"".join(self.frames))
        wf.close()
        logging.info(f"Recording saved to {self.filepath}")

    def rename_audio(self, new_name):
        if not self.filepath or not os.path.exists(self.filepath):
            logging.error("No audio file exists to rename")
            return False
        
        directory = os.path.dirname(self.filepath)
        new_filepath = os.path.join(directory, f"{new_name}.wav")
        
        try:
            shutil.move(self.filepath, new_filepath)
            self.filepath = new_filepath
            logging.info(f"Audio file renamed to {new_filepath}")
            return True
        except Exception as e:
            logging.error(f"Error renaming audio file: {e}")
            return False
