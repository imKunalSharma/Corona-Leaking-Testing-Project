import RPi.GPIO as GPIO

BUTTON_PIN = 

GPIO.setmode(GPIO.BCM)

# Remove the internal pull-up resistor, and rely on external pull-up or pull-down
GPIO.setup(BUTTON_PIN, GPIO.IN)  # No pull-up or pull-down

print('Current value of pin', BUTTON_PIN, 'is', GPIO.input(BUTTON_PIN))

# Clean up GPIO resources at the end of the program
GPIO.cleanup()
