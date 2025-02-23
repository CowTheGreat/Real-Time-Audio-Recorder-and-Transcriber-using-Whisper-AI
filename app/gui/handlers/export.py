import csv
import json
from tkinter import filedialog, messagebox
def export_transcription(transcriber):
    """
    Exports the current transcription segments (from transcriber.segments_with_confidence)
    to JSON or CSV with time stamps.
    """
    # Check if transcription data is available
    if not hasattr(transcriber, "segments_with_confidence") or not transcriber.segments_with_confidence:
        messagebox.showwarning("Export Error", "No transcription data available to export.")
        return

    # Ask the user to select format (Yes = JSON, No = CSV)
    fmt_choice = messagebox.askquestion("Select Format", "Export as JSON? (Select 'No' for CSV)")
    export_format = "json" if fmt_choice.lower() == "yes" else "csv"
    file_extension = ".json" if export_format == "json" else ".csv"

    # Open a file save dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=file_extension,
        filetypes=[("JSON Files", "*.json")] if export_format == "json" else [("CSV Files", "*.csv")],
        title="Save Transcription Export"
    )
    if not file_path:
        return  # User cancelled

    try:
        data = transcriber.segments_with_confidence  # List of dictionaries with transcription details
        if export_format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        else:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["timestamp", "text", "confidence"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for segment in data:
                    writer.writerow({
                        "timestamp": segment.get("timestamp", ""),
                        "text": segment.get("text", ""),
                        "confidence": segment.get("confidence", "")
                    })
        messagebox.showinfo("Export Success", f"Transcription exported successfully to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export transcription: {e}")