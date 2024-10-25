from sys import byteorder
from threading import Thread

import serial
import random
import csv

com_port = 'COM10'  # TO-DO, chagne the com port of the FPGA device
baud_rate = 115200  # Don't change this

# Open the COM port
ser = serial.Serial(com_port, baud_rate, timeout=1)

SEED = 0x43984934
input_length = 32
random.seed(SEED)

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
    cmd = input("Enter G to generate 'Good' data or V to validate the data ")
    if (cmd == 'G') | (cmd == 'g'):
        print("Generating...")
        try:
            while True:
                with open('output.csv', 'w', newline='') as file:
                    for i in range(0, 1000):
                        if (i % 100) == 0:
                            print(f"{10*(i / 100)}% done.")
                        # Generate random data
                        rand = random.randint(0, 2 ** input_length - 1)
                        # Send data to the device
                        data_to_send = rand.to_bytes(bytes_to_read, byteorder='big')
                        # data_bytes = bytes.fromhex(data_to_send)
                        ser.write(data_to_send)

                        # Read data from the FPGA
                        received_data = ser.read(
                            bytes_to_read)  # number of bytes is dictated by the global variableL bytes_to_read

                        #write input, output to csv file
                        byte_to_int = int.from_bytes(received_data, byteorder='big')
                        write = csv.writer(file)
                        write.writerow([str(rand), str(byte_to_int)])
                    break
        except KeyboardInterrupt:
            pass
        finally:
            ser.close()
    elif (cmd == 'V') | (cmd == 'v'):
        print("Verifying...")
        i = 0
        with open('output.csv', mode = 'r') as file:
            reader = csv.reader(file)
            for row in file:
                if (i % 100) == 0:
                    print(f"{10 * (i / 100)}% done.")
                i += 1
                text = row.split(',')
                in_rand = int(text[0])
                out_rand = int(text[1])

                # Send data to the device
                data_to_send = in_rand.to_bytes(bytes_to_read, byteorder='big')

                ser.write(data_to_send)
                # Read data from the FPGA
                received_data = ser.read(
                    bytes_to_read)  # number of bytes is dictated by the global variableL bytes_to_read
                byte_to_int = int.from_bytes(received_data, byteorder='big')

                if byte_to_int != out_rand:
                    #Error, or in this case, trojan 0.0
                    # Find the difference in the output
                    # Convert the received bytes to a hexadecimal string
                    result_difference = byte_to_int ^ out_rand
                    incorrect_output.append(result_difference)
                    #store the input
                    incorrect_inputs.append(in_rand)
            if (len(incorrect_output) != 0):
                # and list will have the trigger bits corresponding to a '1'
                and_guy = incorrect_inputs[0]
                # or list will have the trigger bits corresponding to a '0' set to '1'
                or_guy = incorrect_inputs[0]
                for i in range(1, len(incorrect_inputs)):
                    and_guy = and_guy & incorrect_inputs[i]
                    or_guy = or_guy | incorrect_inputs[i]
                trig_result = ~(and_guy ^ or_guy)
                for i in range(0, 32):
                    bit = (trig_result >> i) & 0x01
                    if bit == 1:
                        # We have a trigger input, check the or list to see if its a 0
                        bit_or = (or_guy >> i) & 0x01
                        if bit_or == 0:
                            # Then the bit we found was a 0 trigger
                            print(f"Bit {i} is a 0 for the trigger")
                        else:
                            # The bit we found was a 1 trigger
                            print(f"Bit {i} is a 1 for the trigger")
                # Check for the payload bit on the output
                payload = incorrect_output[0]
                for i in range(0, 32):
                    pay_bit = (payload >> i) & 0x01
                    if pay_bit == 1:
                        # We have a bit changed by the payload
                        print(f"Bit {i} is changed in the payload")
            print("Connection closed.")
            ser.close()

    else:
        print("Incorrect command ")
        exit(1)
else:
    print(f"Failed to connect to {com_port}")

