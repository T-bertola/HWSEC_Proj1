from sys import byteorder
from threading import Thread

import serial
import random

com_port = 'COM9'  # TO-DO, chagne the com port of the FPGA device
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

            for i in range(0,2000):
                rand = random.randint(0, 2**32 - 1)
                a = (int(rand) & 0xFFFF0000) >> 16
                b = (int(rand) & 0x0000FFFF)
                result = a * b
                # Send data to the device
#                result_hex = result.to_bytes(bytes_to_read, byteorder='big')
#                hex_string_result = ''.join(f'{byte:02X}' for byte in result_hex)
#                a_hex = ''.join(f'{byte:02X}' for byte in a.to_bytes(bytes_to_read, byteorder='big'))
#                b_hex = ''.join(f'{byte:02X}' for byte in b.to_bytes(bytes_to_read, byteorder='big'))
#                print(f"The expected result of {a_hex} * {b_hex} is: {hex_string_result}")
                data_to_send = rand.to_bytes(bytes_to_read, byteorder='big')
               # data_bytes = bytes.fromhex(data_to_send)
                ser.write(data_to_send)

                # Read data from the FPGA
                received_data = ser.read(
                    4)  # to-do, change the parameter into the number of bytes needed to read from FPGA

                # Convert the received bytes to a hexadecimal string
#                hex_string = ''.join(f'{byte:02X}' for byte in received_data)

                # Print the received data as a hexadecimal string
#                print(f"The Actual result of {a} * {b} is: {hex_string}")

                byte_to_int = int.from_bytes(received_data, byteorder='big')
                if byte_to_int != result:
                    #Error, or in this case, trojan 0.0
                    # Find the difference in the output
                    # Convert the received bytes to a hexadecimal string
                    #hex_string = ''.join(f'{byte:02X}' for byte in received_data)

                    # Print the received data as a hexadecimal string
                   # print(f"The Actual result of {a} * {b} is: {hex_string}")
                    result_difference = byte_to_int ^ result
                    incorrect_output.append(result_difference)
                    #store the input
                    incorrect_inputs.append(rand)
            break




    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        and_guy = incorrect_inputs[0]
        or_guy = incorrect_inputs[0]
        for i in range(1, len(incorrect_inputs)):
            and_guy = and_guy & incorrect_inputs[i]
            or_guy = or_guy | incorrect_inputs[i]
        trig_result = ~(and_guy^or_guy)
        for i in range (0,32):
            bit = (trig_result >> i) & 0x01
            if bit == 1 :
                #We have a trigger input, check the or list to see if its a 0
                bit_or =  (or_guy >> i) & 0x01
                if bit_or == 0:
                    #Then the bit we found was a 0 trigger
                    print(f"Bit {i} is a 0 for the trigger")
                else:
                    print(f"Bit {i} is a 1 for the trigger")

        print("Connection closed.")
else:
    print(f"Failed to connect to {com_port}")

