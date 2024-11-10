import sys
import cv2
import numpy as np
import pyautogui
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QComboBox, QFileDialog
from PyQt5.QtCore import QTimer, Qt

class ScreenRecorderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Recorder")
        self.setGeometry(100, 100, 400, 300)
        
        self.recording = False
        self.frame_count = 0
        self.out = None
        self.start_time = None
        self.save_path = None  # To store the save location
        self.elapsed_time = 0  # To keep track of elapsed recording time

        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.record_frame)

        # Timer for updating the display of recording time
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

        self.stop_button = QPushButton("Stop Recording", self)
        self.stop_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_button)

        self.resolution_combo = QComboBox(self)
        self.resolution_combo.addItem("1920x1080")
        self.resolution_combo.addItem("1280x720")
        self.resolution_combo.addItem("1024x768")
        self.resolution_combo.setCurrentIndex(0)
        layout.addWidget(self.resolution_combo)

        self.save_button = QPushButton("Choose Save Location", self)
        self.save_button.clicked.connect(self.choose_save_location)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def toggle_recording(self):
        if not self.recording:
            if self.save_path:  # Check if a save location is selected
                self.start_recording()
                self.record_button.setText("Pause Recording")
                self.display_timer.start(1000)  # Start display timer for elapsed time
            else:
                print("Please choose a save location first.")
        else:
            self.stop_recording()
            self.record_button.setText("Start Recording")
            self.display_timer.stop()

    def start_recording(self):
        self.recording = True
        self.frame_count = 0
        self.elapsed_time = 0  # Reset elapsed time
        self.update_time_display()  # Update time display at start
        self.start_time = time.time()

        # Get screen size from resolution dropdown
        resolution = self.resolution_combo.currentText().split('x')
        width, height = int(resolution[0]), int(resolution[1])

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.out = cv2.VideoWriter(self.save_path, fourcc, 20.0, (width, height))

        self.timer.start(1)  # Start the timer to record frames

    def stop_recording(self):
        self.recording = False
        if self.out:
            self.out.release()
        self.timer.stop()
        self.display_timer.stop()
        self.update_time_display()  # Update time display at stop
        print(f"Recording stopped. Total frames: {self.frame_count}")

    def record_frame(self):
        if self.recording:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize frame based on selected resolution
            resolution = self.resolution_combo.currentText().split('x')
            width, height = int(resolution[0]), int(resolution[1])
            frame = cv2.resize(frame, (width, height))

            self.out.write(frame)
            self.frame_count += 1

    def choose_save_location(self):
        # Use QFileDialog to let the user choose the location and file name
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "AVI Files (*.avi);;All Files (*)", options=options)
        
        if file_name:
            self.save_path = file_name  # Store the chosen file path
            print(f"Saving video to: {self.save_path}")

    def update_time_display(self):
        # Update elapsed time
        if self.recording:
            self.elapsed_time += 1
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            self.time_label.setText(f"Recording Time: {minutes:02}:{seconds:02}")

    def closeEvent(self, event):
        if self.recording:
            self.stop_recording()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorderApp()
    window.show()
    sys.exit(app.exec_())
