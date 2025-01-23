# 🔊 Real-Time-Audio-Recorder-and-Transcriber-using-Whisper-AI

This project is an interactive desktop application that allows users to record audio in real-time, save the recordings, and transcribe the audio to text using the Whisper AI model. The user-friendly interface is built with Tkinter, making it easy to start and stop recordings and generate transcriptions with just a few clicks.

This Python-based GUI application allows you to record audio, save it as a `.wav` file, and transcribe it into text using OpenAI's Whisper model. Built with `tkinter`, it features buttons to start/stop recording and transcribe audio, saving the recording as `output.wav` and the transcription as `transcription.txt`.

## 🔥 Features

1. _Real-Time Audio Recording:_
   Users can start and stop audio recordings with the click of a button. Audio is captured using PyAudio, ensuring high-quality recordings.

2. _Audio File Management:_
   Recorded audio is saved in WAV format for compatibility and quality retention. Automatic file saving upon stopping the recording.

3. _AI-Powered Transcription:_
   Uses Whisper, an advanced speech-to-text model, to transcribe recorded audio. Transcription results are saved to a text file for easy access and further use.

4. _User-Friendly Interface:_
   Built with Tkinter, the application provides a simple, clean, and responsive interface. Buttons are styled for ease of use and accessibility.

## 🛠️ Installation

1. **Fork this repository:** Fork the `CowTheGreat/Real-Time-Audio-Recorder-and-Transcriber-using-Whisper-AI` repository. Follow these instructions on [how to fork a repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

2. **Clone the project:** `git clone git@github.com:your-username/Real-Time-Audio-Recorder-and-Transcriber-using-Whisper-AI`

3. **Required downloads:**

```bash
  cd Real-Time-Audio-Recorder-and-Transcriber-using-Whisper-AI
  pip install -r requirements.txt
```

4. **Alternative ways to download the dependencies:**

- To run, install Python 3.8+ and required packages (`pyaudio` and `whisper`) using

```bash
pip install pyaudio whisper
```

- Whisper downloads its models on the first run; ensure an active internet connection. Customize the Whisper model by modifying `whisper.load_model("small")` in the code (options: tiny, base, small, medium, large).

- For more on Whisper, visit https://github.com/openai/whisper.

5. **Running the project:**
   Run the application with :

```bash
   python ui.py
```

## 🚀 How It Works

- Start Recording: Click the "Start Recording" button to begin capturing audio. The button will be disabled while recording is in progress.
- Stop Recording: Click the "Stop Recording" button to end the audio capture. The application saves the audio to a file and enables the transcription feature.
- Transcribe Audio: Click the "Transcribe" button to convert the recorded audio into text. The transcribed text is saved to a file named transcription.txt.

## 🙌 Contributing

Contributions are always welcome! Whether you want to report an issue, suggest a feature, or submit a pull request, your input is greatly appreciated.

### **To Contribute:**

- Fork this repository.
- Create a new branch for your feature or bug fix (`git checkout -b feature-name`).
- Commit your changes with a clear message.
- Push your branch and open a pull request.

Please ensure your contributions align with the project's goals and follow the coding style. For major changes, kindly open an issue first to discuss your ideas.

Thank you for contributing! 🎉

## 🌟 New Features
### Added Features:
1. Enhanced transcription accuracy using Whisper AI's medium and large models.
2. Integration of a progress bar to track recording duration.
3. Support for multiple audio file formats, including `.mp3` and `.flac`.
4. Dark mode for the user interface.
### Upcoming Features:
1. Language selection for transcription.
2. Option to edit and save transcriptions directly within the application.
3. Cloud storage integration for recordings and transcriptions.
4. Real-time translation alongside transcription.

## 📚 Examples and Tutorials
### Example 1: Recording and Transcription
1. Open the application by running `python ui.py`.
2. Click "Start Recording" and speak into your microphone.
3. Click "Stop Recording" to end the session.
4. Click "Transcribe" to convert the audio into text. The transcription will be saved as `transcription.txt`.
### Example 2: Customizing Whisper Model
- Modify the model in `ui.py` by changing the line:
```bash
   model = whisper.load_model("base")
```
   Replace `base` with `tiny`, `small`, `medium`, or `large` based on your preference.

## ❓ FAQ
### **Q: What if I encounter a "PyAudio installation error"?**

A: Ensure you have installed the appropriate build tools for your operating system. Refer to PyAudio installation guide.

### **Q: Whisper model is not downloading or working?**

A: Check your internet connection and ensure `whisper` is correctly installed. Run `pip install --upgrade whisper` if needed.

### **Q: How can I add support for another language?**

A: Modify the transcription function to include the `language` parameter. For example:
```bash
   result = model.transcribe("output.wav", language="es")
```

## 🛠️ Error-Handling Best Practices
1. **Microphone Not Detected:**
   - Verify your microphone is connected and working.
   - Use `sounddevice` or `pyaudio` to list available devices and select the correct one.
2. **File Save Errors:**
   - Ensure the application has write permissions in the directory.
3. **Transcription Errors:**
   - Use a higher-quality microphone.
   - Switch to a more robust Whisper model (e.g., `medium` or `large`).

## ⭐️ Acknowledgements

A very big thanks to all the contributors for helping this project grow. Your efforts are greatly appreciated!

<a href="https://github.com/CowTheGreat/Real-Time-Audio-Recorder-and-Transcriber-using-Whisper-AI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=CowTheGreat/Real-Time-Audio-Recorder-and-Transcriber-using-Whisper-AI" />
</a>
