import os
import hashlib
import tkinter as tk
from tkinter import messagebox
from ..handlers.customization import update_font_size, choose_color
def open_annotation_window(Window):
    # Create a new top-level window for annotations
    annotation_win = tk.Toplevel(Window['root'])
    annotation_win.title("Annotate Transcription")
    annotation_win.geometry("600x400")

    # Create a frame for layout
    frame = tk.Frame(annotation_win, padx=10, pady=10, bg="#2b2b2b")
    frame.pack(fill=tk.BOTH, expand=True)

    # Label for transcription display
    transcription_label = tk.Label(frame, text="Transcription", bg="#2b2b2b", fg="white", font=("Helvetica", 12, "bold"))
    transcription_label.pack(anchor="w")

    font_size_label = tk.Label(Window['control_frame'], text="Font Size:", bg="#2b2b2b", fg="white")
    font_size_label.pack(side=tk.LEFT, padx=5)

    font_sizes = [8, 10, 11, 12, 14, 16, 18, 20]
    font_size_var = tk.IntVar(value=11)  # Default size matches initial setting
    font_size_dropdown = tk.OptionMenu(Window['control_frame'], font_size_var, *font_sizes, command=lambda:update_font_size(Window['transcription_box']))
    font_size_dropdown.config(bg="#4caf50", fg="white", activebackground="#45a049")
    font_size_dropdown.pack(side=tk.LEFT, padx=5)

    color_button = tk.Button(
        Window['control_frame'], 
        text="Choose Color", 
        command=lambda:choose_color(Window['transcription_box']),
        bg="#4caf50",
        fg="white",
        activebackground="#45a049"
    )
    color_button.pack(side=tk.LEFT, padx=5)

    # Adding tooltips for better UX
    def create_tooltip(widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.wm_overrideredirect(True)
        
        label = tk.Label(tooltip, text=text, bg="#ffffe0", relief="solid", borderwidth=1)
        label.pack()
        
        def enter(event):
            x = widget.winfo_rootx() + widget.winfo_width() + 5
            y = widget.winfo_rooty()
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def leave(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    create_tooltip(font_size_dropdown, "Adjust font size for the transcription text")
    create_tooltip(color_button, "Change base text color for the transcription")
    # Read-only text widget to display the current transcription
    transcription_display = tk.Text(frame, height=10, wrap=tk.WORD)
    transcription_display.pack(fill=tk.BOTH, expand=True, pady=(0,10))
    transcription_text = Window['transcription_box'].get("1.0", tk.END).strip()
    transcription_display.insert(tk.END, transcription_text)
    transcription_display.config(state=tk.DISABLED)

    # Label for annotation input
    annotation_label = tk.Label(frame, text="Enter your comments/annotations:", bg="#2b2b2b", fg="white", font=("Helvetica", 12, "bold"))
    annotation_label.pack(anchor="w")

    # Text widget for user annotations
    annotation_text_widget = tk.Text(frame, height=5, wrap=tk.WORD)
    annotation_text_widget.pack(fill=tk.BOTH, expand=True, pady=(0,10))

    # Function to save annotated transcription
    def save_annotation():
        comments = annotation_text_widget.get("1.0", tk.END).strip()
        if not transcription_text:
            messagebox.showwarning("Warning", "No transcription available to annotate.")
            return

        # Generate a unique filename based on the transcription content
        transcription_hash = hashlib.md5(transcription_text.encode()).hexdigest()[:8]  # Short hash for uniqueness
        annotated_file = os.path.join(Window['save_directory'], f"annotated_transcription_{transcription_hash}.txt")

        # Save both the transcription and the comments
        try:
            with open(annotated_file, "a", encoding="utf-8") as f:
                if os.path.getsize(annotated_file) == 0:  # If it's a new file, add transcription
                    f.write(f"Transcription:\n{transcription_text}\n\n")
                f.write(f"User Comments:\n{comments}\n\n")  # Append new comments
                
            messagebox.showinfo("Success", f"Annotated transcription saved to {annotated_file}")
            annotation_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save annotation: {e}")


    # Save Annotation button
    save_button = tk.Button(frame, text="Save Annotation", command=save_annotation, bg="#4caf50", fg="white", font=("Helvetica", 12, "bold"), bd=3, relief=tk.RAISED)
    save_button.pack(pady=5)