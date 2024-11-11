Usage
Launch the application.
Choose a resolution and save location [Imp.] for the recording.
Click "Start Recording" to begin capturing the screen.
Click "Stop Recording" to save the video and end recording


Code Structure and Functionality
Imports

Imports necessary libraries:
PyQt5 for GUI components.
OpenCV for video writing functionality.
PyAutoGUI for capturing screen frames.
Numpy for handling images as arrays.
ScreenRecorderApp Class

This is the main class of the application, inheriting from QWidget for creating the window.
__init__ Method

Sets up the main window title, size, and icon.
Initializes variables such as recording status, frame_count, save_path, and a timer for capturing frames.
Calls init_ui() to set up the layout and interface elements, including buttons, labels, and dropdowns.
init_ui() Method

Creates and arranges GUI components:
Label for the application title.
Time Label to display the elapsed recording time.
Buttons for starting/stopping recording and setting the save location.
ComboBox for resolution selection.
toggle_recording() Method

Starts or stops recording depending on the current state.
If a save location isn’t set, it displays a message instructing the user to choose one first.
Changes the button text to "Pause Recording" when recording starts.
start_recording() Method

Sets up the recording parameters, including video resolution, codec, and output file path.
Starts a timer to capture frames every millisecond (timer.start(1)).
stop_recording() Method

Stops the recording, releases the video file, stops timers, and displays the total frame count.
record_frame() Method

Captures a screenshot using PyAutoGUI.
Converts and resizes the frame to the selected resolution, then writes it to the video file.
Increments the frame counter.
choose_save_location() Method

Opens a file dialog for the user to choose where to save the video.
Stores the chosen path in self.save_path.
update_time_display() Method

Updates the time_label with the elapsed time, counting minutes and seconds.
closeEvent() Method
Ensures recording stops if the window is closed.
