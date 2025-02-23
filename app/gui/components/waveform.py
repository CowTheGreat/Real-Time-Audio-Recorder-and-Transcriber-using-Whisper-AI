import pyaudio
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading

class WaveformVisualizer:
    def __init__(self, frame):
        self.parent = frame
        self.is_recording = False
        self._create_canvas()
        # Create matplotlib figure
        self.fig = Figure(figsize=(4, 4), dpi=100, facecolor='#2b2b2b')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        # Set up the line plot with matching dimensions
        self.chunk_size = 1024
        self.x = np.arange(0, self.chunk_size)
        self.line, = self.ax.plot(self.x, np.zeros(self.chunk_size), color='#4caf50')
        
        # Configure plot appearance
        self.ax.set_ylim(-32768, 32767)
        self.ax.set_xlim(0, self.chunk_size)
        self.ax.grid(True, color='#444444')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg='#2b2b2b', highlightthickness=0)
        self.canvas_widget.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Audio stream configuration
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.p = None
        self.stream = None

    def start_recording(self):
        self.is_recording = True
        threading.Thread(target=self._record_stream, daemon=True).start()

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

    def _record_stream(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size)
                audio_data = np.frombuffer(data, dtype=np.int16)
                self.line.set_ydata(audio_data)
                self.canvas.draw_idle()
            except Exception as e:
                print(f"Error reading audio stream: {e}")
                break

        self.stop_recording()
    def update_theme(self, theme):
        self.fig.set_facecolor(theme['plot_bg'])
        self.ax.set_facecolor(theme['plot_bg'])
        self.line.set_color(theme['waveform_color'])
        self.ax.tick_params(axis='x', colors=theme['axis_color'])
        self.ax.tick_params(axis='y', colors=theme['axis_color'])
        self.ax.grid(True, color=theme['grid_color'])
        self.ax.xaxis.label.set_color(theme['axis_color'])
        self.ax.yaxis.label.set_color(theme['axis_color'])
        self.ax.title.set_color(theme['axis_color'])
        self.canvas.draw()
    def _create_canvas(self):
        self.fig = Figure(figsize=(4, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot(np.arange(0, 1024), np.zeros(1024))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.get_tk_widget().pack()