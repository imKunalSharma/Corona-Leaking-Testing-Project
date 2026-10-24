import RPi.GPIO as GPIO
import time

# Pin configuration (using BCM numbering)
INPUT_PINS = [19, 13, 6, 5] # Example pins for an 8-bit input
NUM_BITS = 4

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    for pin in INPUT_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Use pull-down resistors

def read_gpio_as_int():
    """Reads the state of all configured GPIO pins and converts to a single integer."""
    value = 0
    # Read pins from most significant bit to least significant bit
    for i, pin in enumerate(INPUT_PINS):
        if GPIO.input(pin) == GPIO.HIGH:
            # Set the corresponding bit in the integer
            # The left-most pin corresponds to the most significant bit
            value |= (1 << (NUM_BITS - 1 - i))
    return value

def reverse_bits(n, width):
    """Reverses the bits of an integer for a given width."""
    # Convert integer to a zero-padded binary string, reverse the string, and convert back to int
    binary_str = format(n, '0%db' % width)
    reversed_str = binary_str[::-1]
    reversed_int = int(reversed_str, 2)
    return reversed_int

# Main logic
try:
    setup_gpio()
    while True:
        # 1. Read GPIO inputs and convert to an integer
        input_value = read_gpio_as_int()

        # 2. Reverse the bits of the resulting integer
        reversed_value = reverse_bits(input_value, NUM_BITS)

        print(f"Original Value (Dec): {input_value} (Bin: {format(input_value, '08b')})")
        print(f"Reversed Value (Dec): {reversed_value} (Bin: {format(reversed_value, '08b')})")
        print("-" * 20)
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up GPIO settings when the script is stopped
    GPIO.cleanup()
    print("GPIO cleaned up")
except RuntimeError as e:
    print(f"Error importing RPi.GPIO: {e}")
