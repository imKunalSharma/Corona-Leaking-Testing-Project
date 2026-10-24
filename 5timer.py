import sys
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QProgressBar, QLabel)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal


class TimerThread(QThread):
    """
    A thread to run the timer without blocking the GUI.
    """
    update_progress_signal = pyqtSignal(int)
    timer_complete_signal = pyqtSignal()

    def __init__(self, duration_sec):
        super().__init__()
        self.duration_sec = duration_sec
        self.is_running = False

    def run(self):
        self.is_running = True
        start_time = time.time()
        while self.is_running:
            elapsed_time = time.time() - start_time
            if elapsed_time >= self.duration_sec:
                self.update_progress_signal.emit(100)
                self.timer_complete_signal.emit()
                break

            progress = int((elapsed_time / self.duration_sec) * 100)
            self.update_progress_signal.emit(progress)
            time.sleep(0.1)  # Update every 0.1 seconds

    def stop(self):
        self.is_running = False


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sequential Timers")

        self.start_button = QPushButton("Start Timers")
        self.start_button.clicked.connect(self.start_timers)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.status_label = QLabel("Ready")

        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.timer_durations = [5, 7, 3, 6, 4]  # Durations in seconds for each timer
        self.timer_index = 0
        self.timer_thread = None
        self.total_duration = sum(self.timer_durations)  # Total duration of all timers
        self.elapsed_time_all_timers = 0  # Keep track of elapsed time across all timers

    def start_timers(self):
        self.timer_index = 0
        self.elapsed_time_all_timers = 0  # Reset elapsed time
        self.start_next_timer()

    def start_next_timer(self):
        if self.timer_index < len(self.timer_durations):
            duration = self.timer_durations[self.timer_index]
            self.status_label.setText(f"Timer {self.timer_index + 1}/{len(self.timer_durations)} running for {duration} seconds")
            self.progress_bar.setValue(int((self.elapsed_time_all_timers / self.total_duration) * 100))  # Initial progress

            self.timer_thread = TimerThread(duration)
            self.timer_thread.update_progress_signal.connect(self.update_progress)
            self.timer_thread.timer_complete_signal.connect(self.timer_complete)
            self.timer_thread.start()
        else:
            self.status_label.setText("All timers complete!")
            self.progress_bar.setValue(100)  # Set to 100% when all timers are done
            self.start_button.setEnabled(True)  # Re-enable the start button

    def update_progress(self, value):
        # Calculate the overall progress based on the current timer's progress and the elapsed time of previous timers
        current_timer_elapsed = (value / 100) * self.timer_durations[self.timer_index]
        overall_elapsed = self.elapsed_time_all_timers + current_timer_elapsed
        overall_progress = int((overall_elapsed / self.total_duration) * 100)
        self.progress_bar.setValue(overall_progress)

    def timer_complete(self):
        duration = self.timer_durations[self.timer_index]
        self.elapsed_time_all_timers += duration  # Add the duration of the completed timer
        self.status_label.setText(f"Timer {self.timer_index + 1} complete.")
        self.timer_index += 1
        self.start_next_timer()

    def closeEvent(self, event):
        """
        Ensure the thread is stopped when the window is closed.
        """
        if self.timer_thread and self.timer_thread.isRunning():
            self.timer_thread.stop()
            self.timer_thread.wait()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
