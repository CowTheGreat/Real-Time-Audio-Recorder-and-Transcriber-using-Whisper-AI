import google.generativeai as genai
import logging
import os
from dotenv import load_dotenv

class TextProcessor:
    def __init__(self, api_key=None):
        # Load environment variables
        load_dotenv()
        
        # Try to get API key from environment variable if not provided
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                logging.info("Gemini model initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing Gemini model: {e}")
                self.model = None
        else:
            logging.warning("No API key provided. Text processing features will be unavailable.")
            self.model = None

    def set_api_key(self, api_key):
        """Set or update the API key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        try:
            self.model = genai.GenerativeModel('gemini-pro')
            logging.info("Gemini model initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Error initializing Gemini model: {e}")
            self.model = None
            return False

    def summarize_text(self, text):
        """Generate a concise summary of the given text"""
        if not self.model:
            return "Error: Gemini model not initialized. Please set API key first."
        
        try:
            prompt = f"Please provide a concise summary of the following text:\n\n{text}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"

    def query_text(self, text, query):
        """Answer questions about the text"""
        if not self.model:
            return "Error: Gemini model not initialized. Please set API key first."
        
        try:
            prompt = f"""Context: {text}\n\nQuestion: {query}\n\nPlease answer the question based on the context provided above."""
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            return f"Error processing query: {str(e)}"
