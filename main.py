import serial
import sys
import json
import time
from pynput.keyboard import Key, Controller
from contextlib import nullcontext

key_delay = 0.05


def initialize_serial():
    # MAC serial port: /dev/cu.usbmodem14101
    # PC serial port: COM3
    s = serial.Serial(sys.argv[1], 9600)
    print('Serial connection initialized on ' + s.name)
    return ser


def read_json_and_create_mapping():
    print('Reading mapping from ' + sys.argv[2])
    with open(sys.argv[2]) as f:
        json_data = json.load(f)

    mappings = {}
    for mapping in json_data.mappings:
        for state in mapping.states:
            key = mapping.id + ':' + state
            print('Setting up mapping for ' + key)
            mappings[key] = mapping

    return mappings


def key_press(mapping):
    if 'SHIFT' in mapping.modifiers:
        shift_context = keyboard.pressed(Key.shift)
    else:
        shift_context = nullcontext

    if 'ALT' in mapping.modifiers:
        alt_context = keyboard.pressed(Key.alt)
    else:
        alt_context = nullcontext

    if 'CTRL' in mapping.modifiers:
        ctrl_context = keyboard.pressed(Key.ctrl)
    else:
        ctrl_context = nullcontext

    with shift_context:
        with alt_context:
            with ctrl_context:
                keyboard.press(mapping.key)
                time.sleep(key_delay)
                keyboard.release(mapping.key)


# Initialize everything
keyboard = Controller()
ser = initialize_serial()
key_mappings = read_json_and_create_mapping()

# Run a loop that reads from serial
while True:
    line = ""
    try:
        # Read line from serial and pull apart the command by :
        line = ser.readline().decode('UTF-8')
        print('Serial input received: ' + line)
    except serial.SerialException:
        print('Serial error detected!')

    # Grab the correct mapping
    key_mapping = key_mappings[line]
    if key_mapping is None:
        print('No mapping found for ' + line)
        continue

    # Use the mapping to press the key
    print("Activating mapping for: " + key_mapping.name)
    key_press(key_mapping)


ser.close()
