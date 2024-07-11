Kent's 2024 Solar Car Code.

Written in collaboration with David Zhou, a St. Mark's School alum.

Run the code by installing the requirements and running the main loop of gui.py.

Intended to run on a LattePanda running Windows installed on the solar car. 

The LattePanda is connected to a cell signal through a 5G modem. A screen displays the GUI and cameras to the driver.

data_capture.py handles the serial communication with a GPS module and the solar panels. It also fetches GPIO sensors from the onboard Arduino using the telemetrix library. 

The two camera streams, front and back, along with the GUI, are intended to be streamed to a streaming platform for live monitoring of the car during the race and record a VOD.
