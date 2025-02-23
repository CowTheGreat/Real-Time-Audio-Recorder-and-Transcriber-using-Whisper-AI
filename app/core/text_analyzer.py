import spacy
from collections import Counter, defaultdict
import logging
from typing import Dict

# Download required spaCy model
try:
    spacy.load("en_core_web_sm")
except OSError:
    logging.info("Downloading spaCy model...")
    import os
    os.system("python -m spacy download en_core_web_sm")

class TextAnalyzer:
    def __init__(self):
        """Initialize the TextAnalyzer with required models and resources."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.info("Downloading spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        logging.info("Text analyzer initialized successfully")

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze the text and return key topics, frequent words, and entities.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Dictionary containing analysis results
        """
        if not text:
            return {
                "frequent_words": [],
                "key_phrases": [],
                "entities": [],
                "word_count": 0
            }

        try:
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Get word frequency (excluding stop words and punctuation)
            words = [token.text.lower() for token in doc 
                    if not token.is_stop and not token.is_punct and token.is_alpha]
            word_freq = Counter(words)
            frequent_words = word_freq.most_common(10)
            
            # Extract key phrases using noun chunks
            key_phrases = list(set([
                chunk.text.lower() for chunk in doc.noun_chunks 
                if len(chunk.text.split()) > 1  # Only phrases with 2+ words
            ]))[:10]
            
            # Extract named entities
            entities = defaultdict(list)
            for ent in doc.ents:
                entities[ent.label_].append(ent.text)
            
            # Format entities for display
            formatted_entities = [
                f"{label}: {', '.join(texts)}"
                for label, texts in entities.items()
            ]

            return {
                "frequent_words": frequent_words,
                "key_phrases": key_phrases,
                "entities": formatted_entities,
                "word_count": len(words)
            }
            
        except Exception as e:
            logging.error(f"Error in text analysis: {str(e)}")
            raise

    def format_analysis_results(self, analysis: Dict) -> str:
        """
        Format the analysis results into a readable string.
        
        Args:
            analysis (dict): Analysis results from analyze_text
            
        Returns:
            str: Formatted analysis results
        """
        output = []
        
        # Add word count
        output.append(f"Total Words (excluding stop words): {analysis['word_count']}\n")
        
        # Add frequent words
        output.append("Most Frequent Words:")
        for word, count in analysis['frequent_words']:
            output.append(f"  • {word}: {count} times")
        output.append("")
        
        # Add key phrases
        if analysis['key_phrases']:
            output.append("Key Phrases:")
            for phrase in analysis['key_phrases']:
                output.append(f"  • {phrase}")
            output.append("")
        
        # Add entities
        if analysis['entities']:
            output.append("Named Entities:")
            for entity in analysis['entities']:
                output.append(f"  • {entity}")
        
        return "\n".join(output)
