import logging
from tkinter import colorchooser
def update_font_size(transcription_box,new_size):
    """Update font size for the transcription box"""
    current_font = transcription_box.cget("font")
    font_family = current_font[0] if isinstance(current_font, tuple) else "Helvetica"
    new_font = (font_family, new_size)
    transcription_box.config(font=new_font)
    logging.info(f"Font size updated to {new_size}")

def choose_color(transcription_box):
    """Open color picker and set text color"""
    color = colorchooser.askcolor(title="Choose Text Color")
    if color[1]:  # User selected a color
        transcription_box.config(fg=color[1])
        logging.info(f"Text color changed to {color[1]}")