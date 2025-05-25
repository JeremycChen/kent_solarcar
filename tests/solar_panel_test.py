import serial

data = {
            "speed": 0,
            "distance": 0,
            "temperature": 0,
            "time": 0,
            "battery": 0,
            "lap": 0,
            'V': 0,
            'I': 0,
            'PPV': 0,
            "gps": [0,0],
        }

solar_panel_1_serial = serial.Serial('COM20', 19200)
solar_panel_2_serial = serial.Serial('COM10', 19200)

def read_serial_data(ser):
    data = {}
    try:
        line = ser.readline().decode('latin-1').strip()
        print(line)
        line_key, line = line.split('\t')
        data[line_key] = line
            
    except Exception as e:
        print(f"Failed to read data from serial port: {e}")
    return data

while True:
    data1 = read_serial_data(solar_panel_1_serial)
    data2 = read_serial_data(solar_panel_2_serial)

    print(data1)
    print(data2)

    # Combine the data
    try:
        data['V'] = data1['V']  # V should be the same for both panels
        if data1['I'] != 'NA' and data2['I'] != 'NA':
            data['I'] = float(data1['I']) + float(data2['I'])

        if data1['PPV'] != 'NA' and data2['PPV'] != 'NA':
            data['PPV'] = float(data1['PPV']) + float(data2['PPV'])
    
    except Exception as e:
        print(f"Failed to update solar panel data: {e}")
        

    print(data)