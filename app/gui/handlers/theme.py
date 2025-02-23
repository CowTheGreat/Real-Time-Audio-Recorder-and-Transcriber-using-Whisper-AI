import tkinter as tk
import seaborn as sns
from app.utils.config import get_styles
styles=get_styles()
def apply_theme(Theme,theme):
    # Update root and main frames
    Theme['root'].configure(bg=theme['bg'])
    Theme['main_frame'].configure(bg=theme['bg'])
    Theme['button_container'].configure(bg=theme['bg'])
    Theme['waveform_frame'].configure(bg=theme['bg'])
    Theme['transcription_frame'].configure(bg=theme['bg'])
    Theme['text_container'].configure(bg=theme['bg'])
    
    # Update all buttons in button_container
    for widget in Theme['button_container'].winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(bg=theme['button_bg'], fg=theme['button_fg'])
    
    # Update text boxes
    Theme['log_box'].config(bg=theme['text_bg'], fg=theme['text_fg'])
    Theme['transcription_box'].config(bg=theme['text_bg'], fg=theme['text_fg'])
    
    # Update labels
    Theme['transcription_label'].config(bg=theme['bg'], fg=theme['fg'])
    Theme['hotkey_label'].config(bg=theme['bg'], fg=theme['fg'])
    
    # Update control_frame and its children
    Theme['control_frame'].configure(bg=theme['bg'])
    for child in Theme['control_frame'].winfo_children():
        if isinstance(child, tk.Label):
            child.config(bg=theme['bg'], fg=theme['fg'])
    
    # Update waveform visualizer
    Theme['visualizer'].update_theme(theme)
    
    # Update seaborn style
    sns.set_style("darkgrid" if theme == styles['dark_theme'] else "whitegrid")

def toggle_theme(Theme):
    current_theme = Theme['current_theme']
    current_theme = styles['light_theme'] if current_theme == styles['dark_theme'] else styles['dark_theme']
    Theme['current_theme']=current_theme
    apply_theme(Theme,current_theme)