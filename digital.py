from telemetrix import telemetrix
import time
import sys

curr_temp = 0.0


def dht(my_board, pin, callback, dht_type):
    print ("...")

    my_board.set_pin_mode_dht(pin, callback, dht_type)
    print ("?%")



def the_callback(data):
    print ("@")

    if data[1]:
        # error message
        
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[4]))
        print(f'DHT Error Report:'
              f'Pin: {data[2]} DHT Type: {data[3]} Error: {data[1]}  Time: {date}')
    else:
        curr_temp = data[5]
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[6]))
        print(f'DHT Valid Data Report:'
              f'Pin: {data[2]} DHT Type: {data[3]} Humidity: {data[4]} Temperature:'
              f' {data[5]} Time: {date}')






board = telemetrix.Telemetrix('COM3',1)
print ("?")
dht(board, 4, the_callback, 11)
print ("!")
