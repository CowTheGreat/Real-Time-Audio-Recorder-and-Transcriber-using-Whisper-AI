import logging
from transformers import pipeline
import librosa
import numpy as np

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class EmotionAnalyzer:
    def __init__(self):
        try:
            # Initialize text emotion analyzer
            self.text_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=3  # Return top 3 emotions
            )
            logging.info("Emotion analyzer initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing emotion analyzer: {e}")
            self.text_classifier = None

    def extract_audio_features(self, audio_path):
        """Extract audio features using librosa"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, duration=3)
            
            # Extract features
            pitch = librosa.yin(y, fmin=librosa.note_to_hz('C2'), 
                              fmax=librosa.note_to_hz('C7'))
            energy = librosa.feature.rms(y=y)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            return {
                'pitch_mean': np.mean(pitch),
                'pitch_std': np.std(pitch),
                'energy_mean': np.mean(energy),
                'tempo': tempo
            }
        except Exception as e:
            logging.error(f"Error extracting audio features: {e}")
            return None

    def analyze(self, text, audio_path=None):
        """Analyze emotions from both text and audio if available"""
        try:
            if not self.text_classifier:
                return "Error: Emotion analyzer not initialized."

            analysis = []  # Store analysis results
            
            # Text analysis
            text_results = self.text_classifier(text)[0]
            analysis.append("\nText-based Emotions:")
            for result in text_results:
                emotion = result['label']
                confidence = result['score']
                percentage = round(confidence * 100, 1)
                analysis.append(f"- {emotion}: {percentage}%")
            
            # Audio analysis if available
            if audio_path:
                audio_features = self.extract_audio_features(audio_path)
                if audio_features:
                    analysis.append("\nVoice Characteristics:")
                    
                    # Analyze pitch variation
                    if audio_features['pitch_std'] > 0.5:
                        analysis.append("- High voice variation detected (possible excitement/stress)")
                    else:
                        analysis.append("- Steady voice detected (possible calmness/control)")
                    
                    # Analyze energy
                    if audio_features['energy_mean'] > 0.7:
                        analysis.append("- High energy level detected (possible excitement/anger)")
                    else:
                        analysis.append("- Low energy level detected (possible calmness/sadness)")
                    
                    # Analyze speaking rate
                    if audio_features['tempo'] > 120:
                        analysis.append("- Fast speaking rate detected (possible excitement/anxiety)")
                    else:
                        analysis.append("- Normal/slow speaking rate detected (possible confidence/sadness)")
            
            return "\n".join(analysis)
            
        except Exception as e:
            logging.error(f"Error during emotion analysis: {e}")
            return "Error: Could not analyze emotions."