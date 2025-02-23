import os
import datetime
import collections
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
def open_new_dashboard(save_directory, root):
    """Opens a modern dashboard window displaying usage statistics from history.txt."""
    history_file = os.path.join(save_directory, "history.txt")
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", "No history file found. Please transcribe some audio first.")
        return

    num_transcriptions = len(lines)
    word_counts = [len(line.split()) for line in lines]
    total_words = sum(word_counts)
    avg_words = total_words / num_transcriptions if num_transcriptions > 0 else 0

    all_words = []
    for line in lines:
        all_words.extend(line.lower().split())
    common_words = collections.Counter(all_words).most_common(5)

    summary_text = (
        f"Total Transcriptions: {num_transcriptions}\n"
        f"Total Words: {total_words}\n"
        f"Average Words per Transcription: {avg_words:.2f}\n"
        f"Last Transcription: {lines[-1][:50] + '...' if lines else 'N/A'}\n"
        f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    dash_win = tk.Toplevel(root)
    dash_win.title("Usage Statistics Dashboard")
    dash_win.geometry("1100x750")  # Increased size for better readability
    dash_win.configure(bg="#2b2b2b")

    title_label = tk.Label(dash_win, text="Usage Statistics Dashboard", bg="#2b2b2b", fg="white", font=("Helvetica", 18, "bold"))
    title_label.pack(pady=10)

    main_frame = tk.Frame(dash_win, bg="#2b2b2b")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    summary_frame = tk.Frame(main_frame, bg="#2b2b2b")
    summary_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    summary_label = tk.Label(summary_frame, text=summary_text, justify="left", bg="#2b2b2b", fg="white", font=("Helvetica", 12))
    summary_label.pack(anchor="n")

    graphs_frame = tk.Frame(main_frame, bg="#2b2b2b")
    graphs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

    sns.set_style("darkgrid", {"axes.facecolor": "#2b2b2b", "grid.color": "gray"})
    fig = plt.Figure(figsize=(12, 8), dpi=100, facecolor="#2b2b2b", constrained_layout=True)

    ax1 = fig.add_subplot(221)
    ax1.bar(range(1, num_transcriptions + 1), word_counts, color="#4CAF50")
    ax1.set_xlabel("Transcription #", color="white")
    ax1.set_ylabel("Word Count", color="white")
    ax1.set_title("Words per Transcription", color="white")
    ax1.tick_params(axis="x", colors="white")
    ax1.tick_params(axis="y", colors="white")

    ax2 = fig.add_subplot(222)
    if common_words:
        labels = [f"{word} ({count})" for word, count in common_words]
        counts = [count for word, count in common_words]
        ax2.pie(counts, labels=labels, colors=sns.color_palette("pastel"), autopct='%1.1f%%', textprops={'color': 'white'})
    ax2.set_title("Frequent Words", color="white")

    ax3 = fig.add_subplot(223)
    sns.histplot(word_counts, bins=15, kde=True, color="#FFA726", ax=ax3)
    ax3.set_xlabel("Word Count", color="white")
    ax3.set_ylabel("Frequency", color="white")
    ax3.set_title("Transcription Length Distribution", color="white")
    ax3.tick_params(axis="x", colors="white")
    ax3.tick_params(axis="y", colors="white")

    ax4 = fig.add_subplot(224)
    ax4.plot(range(1, num_transcriptions + 1), word_counts, marker='o', linestyle='-', color="#FF5722")
    ax4.set_xlabel("Transcription #", color="white")
    ax4.set_ylabel("Word Count", color="white")
    ax4.set_title("Transcription Trend", color="white")
    ax4.tick_params(axis="x", colors="white")
    ax4.tick_params(axis="y", colors="white")

    canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    close_btn = tk.Button(dash_win, text="Close Dashboard", command=dash_win.destroy, bg="#F44336", fg="white", font=("Helvetica", 12, "bold"))
    close_btn.pack(pady=5)