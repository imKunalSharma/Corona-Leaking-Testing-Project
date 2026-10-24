import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import QTimer

class CountdownTimer(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0

    def initUI(self):
        self.setWindowTitle('Countdown Timer')

        self.layout = QVBoxLayout()

        self.label = QLabel('Enter time in seconds:', self)
        self.layout.addWidget(self.label)

        self.time_input = QLineEdit(self)
        self.layout.addWidget(self.time_input)

        self.start_button = QPushButton('Start Timer', self)
        self.start_button.clicked.connect(self.start_timer)
        self.layout.addWidget(self.start_button)

        self.timer_label = QLabel('Time remaining: 0 seconds', self)
        self.layout.addWidget(self.timer_label)

        self.setLayout(self.layout)
        self.setGeometry(100, 100, 300, 200)

    def start_timer(self):
        try:
            self.remaining_time = int(self.time_input.text())
            if self.remaining_time > 0:
                self.timer.start(1000)  # Start timer for 1000 milliseconds (1 second)
                self.timer_label.setText(f'Time remaining: {self.remaining_time} seconds')
            else:
                self.timer_label.setText('Please enter a positive number.')
        except ValueError:
            self.timer_label.setText('Invalid input. Please enter a number.')

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.setText(f'Time remaining: {self.remaining_time} seconds')
        else:
            self.timer.stop()
            self.timer_label.setText('Time is up!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CountdownTimer()
    ex.show()
    sys.exit(app.exec_())