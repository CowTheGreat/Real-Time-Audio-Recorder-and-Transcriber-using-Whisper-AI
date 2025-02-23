import tkinter as tk
button_style = {
    "font": ("Helvetica", 12, "bold"),
    "bg": "#4caf50",
    "fg": "white",
    "activebackground": "#45a049",
    "activeforeground": "white",
    "relief": tk.RAISED,
    "bd": 3,
    "width": 20,
    "height": 1, 
}

dark_theme = {
    'bg': '#2b2b2b',
    'fg': 'white',
    'button_bg': '#4caf50',
    'button_fg': 'white',
    'text_bg': '#333333',
    'text_fg': 'white',
    'plot_bg': '#2b2b2b',
    'plot_fg': 'white',
    'waveform_color': '#4caf50',
    'axis_color': 'white',
    'grid_color': '#444444'
}

light_theme = {
    'bg': '#f0f0f0',
    'fg': 'black',
    'button_bg': '#4caf50',
    'button_fg': 'white',
    'text_bg': 'white',
    'text_fg': 'black',
    'plot_bg': 'white',
    'plot_fg': 'black',
    'waveform_color': '#4caf50',
    'axis_color': 'black',
    'grid_color': '#dddddd'
}
def get_styles():
    return {'dark_theme': dark_theme, 'light_theme': light_theme, 'button_style': button_style}