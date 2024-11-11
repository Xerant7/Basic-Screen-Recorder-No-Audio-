import sys
import cv2
import numpy as np
import pyautogui
import time
import pyaudio
import wave
from threading import Thread
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QComboBox, QFileDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon

# Set the icon for the application window


class ScreenRecorderApp(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Recorder")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowIcon(QIcon("D:\Translator\icon.ico"))
        self.recording = False
        self.audio_recording = False
        self.frame_count = 0
        self.out = None
        self.audio_thread = None
        self.start_time = None
        self.save_path = None
        self.audio_file_path = None
        self.elapsed_time = 0

        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.record_frame)

        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self.update_time_display)

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Screen Recorder", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.time_label = QLabel("Recording Time: 00:00", self)
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)

        self.record_button = QPushButton("Start Recording", self)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        self.record_audio_button = QPushButton("Start Recording with Audio", self)
        self.record_audio_button.clicked.connect(self.toggle_recording_with_audio)
        layout.addWidget(self.record_audio_button)

        self.stop_button = QPushButton("Stop Recording", self)
        self.stop_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_button)

        self.resolution_combo = QComboBox(self)
        self.resolution_combo.addItem("1920x1080")
        self.resolution_combo.addItem("1280x720")
        self.resolution_combo.addItem("1024x768")
        self.resolution_combo.addItem("3840x2160")  # 4K resolution
        self.resolution_combo.addItem("2560x1440")  # 2K resolution
        self.resolution_combo.setCurrentIndex(0)
        layout.addWidget(self.resolution_combo)

        self.save_button = QPushButton("Choose Save Location", self)
        self.save_button.clicked.connect(self.choose_save_location)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def toggle_recording(self):
        if not self.recording:
            if self.save_path:
                self.start_recording()
                self.record_button.setText("Pause Recording")
                self.display_timer.start(1000)
            else:
                print("Please choose a save location first.")
        else:
            self.stop_recording()
            self.record_button.setText("Start Recording")
            self.display_timer.stop()

    def toggle_recording_with_audio(self):
        if not self.recording:
            if self.save_path:
                self.audio_file_path = self.save_path.replace('.avi', '_audio.wav')
                self.audio_thread = Thread(target=self.record_audio)
                self.audio_thread.start()
                self.audio_recording = True
                self.start_recording()
                self.record_audio_button.setText("Pause Recording with Audio")
                self.display_timer.start(1000)
            else:
                print("Please choose a save location first.")
        else:
            self.stop_recording()
            self.record_audio_button.setText("Start Recording with Audio")
            self.display_timer.stop()

    def start_recording(self):
        self.recording = True
        self.frame_count = 0
        self.elapsed_time = 0
        self.update_time_display()
        self.start_time = time.time()

        resolution = self.resolution_combo.currentText().split('x')
        width, height = int(resolution[0]), int(resolution[1])

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.out = cv2.VideoWriter(self.save_path, fourcc, 20.0, (width, height))

        self.timer.start(1)

    def stop_recording(self):
        self.recording = False
        self.audio_recording = False
        if self.out:
            self.out.release()
        self.timer.stop()
        self.display_timer.stop()
        print(f"Recording stopped. Total frames: {self.frame_count}")
        
        if self.audio_thread:
            self.audio_thread.join()
            self.merge_audio_video()

    def record_frame(self):
        if self.recording:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            resolution = self.resolution_combo.currentText().split('x')
            width, height = int(resolution[0]), int(resolution[1])
            frame = cv2.resize(frame, (width, height))

            self.out.write(frame)
            self.frame_count += 1

    def choose_save_location(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "AVI Files (*.avi);;All Files (*)", options=options)
        
        if file_name:
            self.save_path = file_name
            print(f"Saving video to: {self.save_path}")

    def update_time_display(self):
        if self.recording:
            self.elapsed_time += 1
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            self.time_label.setText(f"Recording Time: {minutes:02}:{seconds:02}")

    def record_audio(self):
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 2
        rate = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=sample_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

        frames = []
        while self.audio_recording:
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(self.audio_file_path, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
        print("Audio recording stopped.")

    def merge_audio_video(self):
        import moviepy.editor as mp
        video = mp.VideoFileClip(self.save_path)
        audio = mp.AudioFileClip(self.audio_file_path)
        final_video = video.set_audio(audio)
        final_video.write_videofile(self.save_path.replace('.avi', '_with_audio.avi'))
        print("Merged audio with video.")

    def closeEvent(self, event):
        if self.recording:
            self.stop_recording()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorderApp()
    window.show()
    sys.exit(app.exec_())
