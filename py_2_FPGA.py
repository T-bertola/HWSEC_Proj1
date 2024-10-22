from sys import byteorder
from threading import Thread

import serial
import random

com_port = 'COM10'  # TO-DO, chagne the com port of the FPGA device
baud_rate = 115200  # Don't change this

# Open the COM port
ser = serial.Serial(com_port, baud_rate, timeout=1)

# number of bytes to read, dependent on the circuit implementation
bytes_to_read = 4

incorrect_output = []
incorrect_inputs = []

if ser.is_open:
    print(f"Connected to {com_port} at {baud_rate} baud\n")

    print("""
=================================================================================================   
To send data to the FPGA, input what you want to send out when prompted ! 
You can enter the data with or without the "0x" prefix 

Wait for a second and you should get the output back! It will also be printed out just for you ;) 

*By the way, this program has no idiot check. So, make sure that all of your values are valid
=================================================================================================   
    """)

    try:
        while True:

            for i in range(0,5):
                rand = random.randint(0, 2**32 - 1)
                a = (int(rand) & 0xFFFF0000) >> 16
                b = (int(rand) & 0x0000FFFF)
                result = a * b
                # Send data to the device
                print(f"The expected result of {a} * {b} is: {result}")
                data_to_send = rand.to_bytes(8, byteorder='big')
                data_bytes = bytes.fromhex(data_to_send)
                ser.write(data_bytes)

                # Read data from the FPGA
                received_data = ser.read(
                    bytes_to_read)  # to-do, change the parameter into the number of bytes needed to read from FPGA

                # Convert the received bytes to a hexadecimal string
                hex_string = ''.join(f'{byte:02X}' for byte in received_data)

                # Print the received data as a hexadecimal string
                print(f"The Actual result of {a} * {b} is: {hex_string}")

                byte_to_int = int.from_bytes(received_data, byteorder='big')
                if byte_to_int != result:
                    #Error, or in this case, trojan 0.0
                    # Find the difference in the output
                    result_difference = byte_to_int ^ result
                    incorrect_output.append(result_difference)
                    #store the input
                    incorrect_inputs.append(rand)





    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        print("Connection closed.")
else:
    print(f"Failed to connect to {com_port}")

