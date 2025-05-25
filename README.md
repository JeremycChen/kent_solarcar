Kent's 2025 Solar Car Code.

Written in collaboration with Joe Yu and David Zhou, a Kent School and St. Mark's School alum.

Run the code by installing the requirements and running the main loop of gui.py.

Intended to run on a LattePanda running Windows installed on the solar car. 

The LattePanda is connected to a cell signal through a 5G modem. A screen displays the GUI and cameras to the driver.

data_capture.py handles the serial communication with solar panel charge controllers and a shunt. It also fetches Arduino outputs and controls a normally closed relay. In addition, It also handles CAN bus readouts from the BMSs and the motor.

The two camera streams, front and back, along with the GUI, are intended to be streamed to a streaming platform for live monitoring of the car during the race and record a VOD.
