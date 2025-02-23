import logging
import tkinter as tk
def setup_tkdnd(root):
    try:
        root.tk.eval('package require tkdnd')
        root.tk.call('tkdnd::drop_target', 'register', root, ('DND_Files', 'Files'))
        logging.info("TkDND initialized successfully")
    except tk.TclError as e:
        logging.error(f"Failed to initialize TkDND: {e}")
        # Create a label to show error
        tk.Label(
            root,
            text="Drag and drop not available.\nPlease install python-tkdnd package.",
            bg="#ff6b6b",
            fg="white",
            font=("Helvetica", 10)
        ).pack(fill=tk.X, padx=10, pady=5)
