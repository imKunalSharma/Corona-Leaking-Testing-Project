def binary_to_decimal(binary_str):
    """Converts a binary string to its decimal equivalent."""
    return int(binary_str, 2)

# Get binary input from the user
binary_input = input("Enter a binary number: ")

try:
    # Convert the binary input to decimal
    decimal_output = binary_to_decimal(binary_input)
    print(f"The decimal equivalent of {binary_input} is: {decimal_output}")
except ValueError:
    print("Invalid binary input. Please enter a string containing only 0s and 1s.")