from pyfirmata import Arduino, util
import time

# Connect to Arduino board
board = Arduino('COM3')

# Start iterator thread
it = util.Iterator(board)
it.start()

# Define pin for DHT11 sensor
pin = 4

# Wait for the board to initialize
time.sleep(1)

while True:
    # Read data from DHT11 sensor via Arduino
    temperature = board.analog[0].read()
    humidity = board.analog[1].read()

    # Print sensor readings
    print('Temperature: {0:.2f}°C'.format(temperature))
    print('Humidity: {0:.2f}%'.format(humidity))

    # Wait before taking the next reading
    time.sleep(2)  # Adjust sleep time if needed
