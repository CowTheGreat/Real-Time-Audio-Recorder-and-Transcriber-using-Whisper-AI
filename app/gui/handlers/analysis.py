import os
import logging
import tkinter as tk
from tkinter import simpledialog
def analyze_emotions(Analysis,event=None):
    if not Analysis['recorder'].filepath or not os.path.exists(Analysis['recorder'].filepath):
        logging.warning("No audio file available for emotion analysis.")
        Analysis['transcription_box'].insert(tk.END, "\nNo audio file available for emotion analysis.")
        return
    
    try:
        # Get the current transcription text (excluding confidence scores and formatting)
        current_text = Analysis['transcription_box'].get("1.0", tk.END).strip()
        
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
        emotion_analysis = Analysis['emotion_analyzer'].analyze(clean_text, Analysis['recorder'].filepath)
        
        # Save emotion analysis
        if Analysis['save_directory']:
            emotion_path = os.path.join(Analysis['save_directory'], "emotion_analysis.txt")
        else:
            emotion_path = "emotion_analysis.txt"
            
        with open(emotion_path, "w", encoding="utf-8") as f:
            f.write(f"Emotion Analysis:\n{emotion_analysis}")
        
        # Display in UI
        Analysis['transcription_box'].insert(tk.END, "\n\nEmotion Analysis:\n" + emotion_analysis)
        logging.info(f"Emotion analysis completed and saved to {emotion_path}")
        
    except Exception as e:
        logging.error(f"Error during emotion analysis: {e}")
        Analysis['transcription_box'].insert(tk.END, f"\nError during emotion analysis: {e}")
        
def analyze_text_content(Analysis,event=None):
    """Analyze the transcribed text for key topics and entities."""    
    try:
        # Get the path to the transcription file
        transcription_file = os.path.join(Analysis['save_directory'], "output_transcription.txt") if Analysis['save_directory'] else "output_transcription.txt"
        
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
        analysis_results = Analysis['text_analyzer'].analyze_text(clean_text)
        formatted_results = Analysis['text_analyzer'].format_analysis_results(analysis_results)
        
        # Show results in a new window
        analysis_window = tk.Toplevel(Analysis['root'])
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
        analysis_path = os.path.join(Analysis['save_directory'], "text_analysis.txt") if Analysis['save_directory'] else "text_analysis.txt"
        with open(analysis_path, "w", encoding="utf-8") as f:
            f.write(formatted_results)
        logging.info(f"Text analysis saved to {analysis_path}")
        
    except Exception as e:
        logging.error(f"Error during text analysis: {e}")

def set_api_key(Analysis,event=None):
    api_key = simpledialog.askstring("API Key", "Enter your Gemini API Key:", show='*')
    if api_key:
        success = Analysis['text_processor'].set_api_key(api_key)
        if success:
            logging.info("API key set successfully")
        else:
            logging.error("Failed to initialize with provided API key")

def summarize_text(Analysis,event=None):
    if not Analysis['text_processor'].model:
        logging.error("Please set Gemini API key first")
        return
        
    try:
        # Get text from transcription text widget
        text = Analysis['transcription_box'].get("1.0", tk.END).strip()
        if not text:
            logging.error("No text to summarize")
            return
            
        summary = Analysis['text_processor'].summarize_text(text)
        
        # Show summary in a new window
        summary_window = tk.Toplevel(Analysis['root'])
        summary_window.title("Summary")
        summary_window.geometry("600x400")
        
        summary_text = tk.Text(summary_window, wrap=tk.WORD, height=15, width=60)
        summary_text.pack(padx=10, pady=10, expand=True, fill='both')
        summary_text.insert("1.0", summary)
        summary_text.config(state=tk.DISABLED)
        
    except Exception as e:
        logging.error(f"Error generating summary: {e}")

def query_text(Analysis,event=None):
    if not Analysis['text_processor'].model:
        logging.error("Please set Gemini API key first")
        return
        
    try:
        # Get text from transcription text widget
        text = Analysis['transcription_box'].get("1.0", tk.END).strip()
        if not text:
            logging.error("No text to query")
            return
            
        # Get query from user
        query = simpledialog.askstring("Query", "Enter your question about the text:")
        if not query:
            return
            
        answer = Analysis['text_processor'].query_text(text, query)
        
        # Show answer in a new window
        answer_window = tk.Toplevel(Analysis['root'])
        answer_window.title("Answer")
        answer_window.geometry("600x400")
        
        answer_text = tk.Text(answer_window, wrap=tk.WORD, height=15, width=60)
        answer_text.pack(padx=10, pady=10, expand=True, fill='both')
        answer_text.insert("1.0", answer)
        answer_text.config(state=tk.DISABLED)
        
    except Exception as e:
        logging.error(f"Error processing query: {e}")