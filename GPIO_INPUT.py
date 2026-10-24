import RPi.GPIO as GPIO
import time

# Configure GPIO 17 as an input with pull-up enabled
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Read the input and respond accordingly
while True:
  input_value = GPIO.input(22)
  if input_value == GPIO.HIGH:
    print("Button pressed")
    time.sleep(0.2)  # Debounce the button
  else:
    print("Button released")
    time.sleep(0.2)