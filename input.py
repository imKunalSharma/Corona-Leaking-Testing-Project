import sys
import RPi.GPIO as GPIO
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer

class GPIOApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # Set up GPIO
        self.pins = [19, 13, 6, 5, 9, 10]  # Example GPIO pin numbers
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        for pin in self.pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pins as input with pull-down resistors

        # Set up a timer for auto-refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gpio_states)
        self.timer.start(1000)  # Refresh every 1000 milliseconds (1 second)

        self.update_gpio_states()  # Initial state update

    def initUI(self):
        self.layout = QVBoxLayout()
        
        self.labels = []
        for i in range(6):
            label = QLabel(f'GPIO Pin {i+1}: ')
            self.layout.addWidget(label)
            self.labels.append(label)

        self.button = QPushButton('Refresh States')
        self.button.clicked.connect(self.update_gpio_states)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        self.setWindowTitle('GPIO Input Example')
        self.show()

    def update_gpio_states(self):
        for i, pin in enumerate(self.pins):
            state = GPIO.input(pin)
            self.labels[i].setText(f'GPIO Pin {pin}: {"HIGH" if state else "LOW"}')

    def closeEvent(self, event):
        GPIO.cleanup()  # Clean up GPIO on exit
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GPIOApp()
    sys.exit(app.exec_())
