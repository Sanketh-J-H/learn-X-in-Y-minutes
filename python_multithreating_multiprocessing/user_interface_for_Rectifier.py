# import socket
# import binascii
import datetime  # Import datetime for timestamps

# from openpyxl import Workbook, load_workbook  # Import openpyxl for Excel file handling
import tkinter as tk
from tkinter import ttk
import multiprocessing

# Constants
TOTAL_SIZE = 256  # Total expected size


# Function to calculate CRC-16
def calculate_crc(data):
    """
    Calculate CRC-16 using the specified algorithm.

    :param data: List of data bytes to calculate CRC for.
    :return: Calculated CRC value.
    """
    u16crc = 0xFFFF  # Initial CRC value

    for byte in data:
        u16crc ^= byte  # XOR byte into least significant byte of crc
        for _ in range(8):  # Loop over each bit
            if (u16crc & 0x0001) != 0:  # If the LSB is set
                u16crc >>= 1  # Shift right
                u16crc ^= 0xA001  # XOR with polynomial
            else:
                u16crc >>= 1  # Just shift right

    return u16crc


# Function to unpack the data into the structured format
def unpack_sm_payload(data):
    print(f"256 Byte Full data (hex): {data.hex()}")
    # logger.log_message_txt(f"256 Byte Full data (hex): {data.hex()}")
    # logger.log_message(f"256 Byte Full data (hex): {data.hex()}")

    if len(data) != TOTAL_SIZE:
        print("Received data of unexpected length.")
        # logger.log_message_txt(f"256 Byte Full data (hex): {data.hex()}")
        # logger.log_message(f"256 Byte Full data (hex): {data.hex()}")
        return None

    try:
        # Calculate CRC for the first 254 bytes of data
        received_crc = int.from_bytes(data[254:256], byteorder="big")
        calculated_crc = calculate_crc(data[:254])
        # Reverse the bytes of calculated CRC
        calculated_crc = int.from_bytes(
            calculated_crc.to_bytes(2, byteorder="little")[::-1], byteorder="big"
        )
        if received_crc != calculated_crc:
            print(
                f"CRC mismatch: received {received_crc:04X}, calculated {calculated_crc:04X}"
            )
            # logger.log_message_txt(f"CRC mismatch: received {received_crc:04X}, calculated {calculated_crc:04X}")
            # logger.log_message(f"CRC mismatch: received {received_crc:04X}, calculated {calculated_crc:04X}")
        else:
            print(
                f"Received CRC: {received_crc:04X} match with Calculated CRC: {calculated_crc:04x}"
            )
            # logger.log_message_txt(f"Received CRC: {received_crc:04X} match with Calculated CRC: {calculated_crc:04x}")
            # logger.log_message(f"Received CRC: {received_crc:04X} match with Calculated CRC: {calculated_crc:04x}")

        # Store the first 20 bytes separately
        header = data[:20]
        print(f"First 20 bytes (header): {header.hex()}")
        # logger.log_message_txt(f"First 20 bytes (header): {header.hex()}")
        # logger.log_message(f"First 20 bytes (header): {header.hex()}")

        print(f"First 20 bytes (ASCII): {header.decode('ascii', 'ignore')}")
        # logger.log_message_txt(f"First 20 bytes (ASCII): {header.decode('ascii', 'ignore')}")
        # logger.log_message(f"First 20 bytes (ASCII): {header.decode('ascii', 'ignore')}")

        # Process the rest of the data from byte 21 to 256
        payload = data[20:]
        print(f"Payload data (hex): {payload.hex()}")
        # logger.log_message_txt(f"Payload data (hex): {payload.hex()}")
        # logger.log_message(f"Payload data (hex): {payload.hex()}")

        # Parse string, PMActiveBit, and reserved_PMActiveBit
        reserved_PMActiveBit = data[20:23]
        PMActiveBit = data[23:24]

        print(f"PMActiveBit (Byte): {PMActiveBit.hex()}")
        # logger.log_message_txt(f"PMActiveBit (Byte): {PMActiveBit.hex()}")
        # logger.log_message(f"PMActiveBit (Byte): {PMActiveBit.hex()}")

        low_nibble = PMActiveBit[0] & 0x0F  # Extract low nibble bits
        low_nibble_binary = bin(low_nibble)[2:].zfill(
            4
        )  # Convert to binary and ensure 4 bits
        print(f"PMActiveBit (Low Nibble - Binary): {low_nibble_binary}")
        # logger.log_message_txt(f"PMActiveBit (Low Nibble - Binary): {low_nibble_binary}")
        # logger.log_message(f"PMActiveBit (Low Nibble - Binary): {low_nibble_binary}")

        def parse_power_module(start_byte):
            ambient_temp = int.from_bytes(
                data[start_byte + 2 : start_byte + 4], byteorder="little"
            )
            current = (
                int.from_bytes(
                    data[start_byte + 4 : start_byte + 6], byteorder="little"
                )
                / 10.0
            )
            voltage = (
                int.from_bytes(
                    data[start_byte + 6 : start_byte + 8], byteorder="little"
                )
                / 10.0
            )
            return {
                "module_status_flag_1": data[start_byte : start_byte + 1],
                "module_status_flag_2": data[start_byte + 1 : start_byte + 2],
                "ambient_temperature_hex": data[start_byte + 2 : start_byte + 4][
                    ::-1
                ].hex(),
                "ambient_temperature": ambient_temp,
                "current_hex": data[start_byte + 4 : start_byte + 6][
                    ::-1
                ].hex(),  # MSB to LSB
                "current": current,
                "voltage_hex": data[start_byte + 6 : start_byte + 8][
                    ::-1
                ].hex(),  # MSB to LSB
                "voltage": voltage,
                "reserved": data[start_byte + 8 : start_byte + 16],
            }

        power_modules = []
        for i in range(7):
            start_byte = 24 + i * 16
            power_modules.append(parse_power_module(start_byte))

        # Process charging related info
        demand_voltage = int.from_bytes(data[140:144], byteorder="little") / 10.0
        demand_current = int.from_bytes(data[144:148], byteorder="little") / 10.0
        charging_current = (
            int.from_bytes(data[152:154], byteorder="little") / 10.0
        )  # Combine low and high charging voltage
        charging_voltage = (
            int.from_bytes(data[154:156], byteorder="little") / 10.0
        )  # Combine low and high charging current

        charging_state_count = data[139:140][0]
        contactor_status = (charging_state_count >> 4) & 0x0F  # Extract high nibble bit
        charging_state = charging_state_count & 0x0F  # Extract low nibble decimal

        reserved_1 = data[138:139][0]
        reserved_high_nibble = (reserved_1 >> 4) & 0x0F  # High nibble
        charge_enable_bit = reserved_1 & 0x01  # 0th bit
        reserved_low_bits = (reserved_1 >> 1) & 0x07  # Bits 1-3

        charging_related_info = {
            "battery_SOC": data[136:137],
            "battery_SOH": data[137:138],
            "reserved_1": data[138:139],
            "charging_state_count": data[139:140],
            "charging_state": charging_state,
            "contactor_status": format(contactor_status, "04b"),
            "demand_voltage_hex": data[140:144][::-1].hex(),  # MSB to LSB
            "demand_voltage": demand_voltage,
            "demand_current_hex": data[144:148][::-1].hex(),  # MSB to LSB
            "demand_current": demand_current,
            "positive_gun_temperature": data[148:149],
            "negative_gun_temperature": data[149:150],
            "reserved_2": data[150:152],
            "charging_current_hex": data[152:154][::-1].hex(),  # MSB to LSB
            "charging_current": charging_voltage,
            "charging_voltage_hex": data[154:156][::-1].hex(),  # MSB to LSB
            "charging_voltage": charging_current,
            "charging_time_minute": data[156:157],
            "charging_time_hour": data[157:158],
            "reserved_3": data[158:160],
            "BST_reason": data[160:162],
            "CST_reason": data[162:164],
            "energy_data": data[164:168],
            "reserved_high_nibble": reserved_high_nibble,
            "charge_enable_bit": charge_enable_bit,
            "reserved_low_bits": reserved_low_bits,
        }

        padding = data[168:254]
        CRC1 = data[254:255]
        CRC2 = data[255:256]

        return {
            "header": header,
            "PMActiveBit": PMActiveBit,
            "reserved_PMActiveBit": reserved_PMActiveBit,
            "power_modules": power_modules,
            "charging_related_info": charging_related_info,
            "padding": padding,
            "CRC1": CRC1,
            "CRC2": CRC2,
        }
    except ValueError as e:
        print(f"Error converting hexadecimal data: {e}")
        return None


def start_client(queue):
    # server_ip = "192.168.11.51"  # Server IP address
    # server_port = 3333  # Server port number
    # try:
    #     # Create a socket object
    #     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_socket.connect((server_ip, server_port))
    #     print(f"Connected to server {server_ip}:{server_port}")
    # logger.log_message_txt(f"Connected to server {server_ip}:{server_port}")
    # logger.log_message(f"Connected to server {server_ip}:{server_port}")

    while True:
        string_data = "0101000053756e4d6f6220546563682e2e2e0000000000030000f400f201220f00000000000000000000f400f401230f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001d00015558110000f401000000000000e603220f00000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009dd2"  # Expecting 256 bytes of data
        data = bytes.fromhex(string_data)
        # data = client_socket.recv(TOTAL_SIZE)  # Expecting 256 bytes of data
        if not data:
            break
        if len(data) == TOTAL_SIZE:
            try:
                payload = unpack_sm_payload(data)
                if payload is None:
                    continue

                # Print header
                # print(f"Header (hex): {payload['header'].hex()}")
                # logger.log_message_txt(f"Header (hex): {payload['header'].hex()}")
                # logger.log_message(f"Header (hex): {payload['header'].hex()}")
                # print(f"Header (ASCII): {payload['header'].decode('ascii', 'ignore')}")
                # logger.log_message_txt(f"Header (ASCII): {payload['header'].decode('ascii', 'ignore')}")
                # logger.log_message(f"Header (ASCII): {payload['header'].decode('ascii', 'ignore')}")

                # Print parsed data
                # print(
                #     f"Reserved PM Active Bit: {payload['reserved_PMActiveBit'].hex()}"
                # )
                # logger.log_message_txt(f"Reserved PM Active Bit: {payload['reserved_PMActiveBit'].hex()}")
                # logger.log_message(f"Reserved PM Active Bit: {payload['reserved_PMActiveBit'].hex()}")

                # Assuming the previous `Logger` class is still in place

                # Inside the 'unpack_sm_payload' or similar function, logging added for each print statement

                # Charging Related Info Logging
                charging_info = payload["charging_related_info"]
                # print("Charging Related Info:")
                # logger.log_message("Charging Related Info:")
                # logger.log_message_txt("Charging Related Info:")

                soc = int(
                    charging_info["battery_SOC"].hex(), 16
                )  # Convert hex to decimal
                soh = int(
                    charging_info["battery_SOH"].hex(), 16
                )  # Convert hex to decimal

                # print(
                #     f"  Battery SOC: {charging_info['battery_SOC'].hex()} ({int(charging_info['battery_SOC'].hex(), 16)})"
                # )
                # logger.log_message(f"  Battery SOC: {charging_info['battery_SOC'].hex()} ({int(charging_info['battery_SOC'].hex(), 16)})")
                # logger.log_message_txt(f"  Battery SOC: {charging_info['battery_SOC'].hex()} ({int(charging_info['battery_SOC'].hex(), 16)})")

                # print(
                #     f"  Battery SOH: {charging_info['battery_SOH'].hex()} ({int(charging_info['battery_SOH'].hex(), 16)})"
                # )
                # logger.log_message(f"  Battery SOH: {charging_info['battery_SOH'].hex()} ({int(charging_info['battery_SOH'].hex(), 16)})")
                # logger.log_message_txt(f"  Battery SOH: {charging_info['battery_SOH'].hex()} ({int(charging_info['battery_SOH'].hex(), 16)})")
                temp_values = []
                current_values = []
                voltage_values = []
                # print(f"pm values :{payload['power_modules']}")
                # For each power module, logging both in text and Excel
                # For each power module, logging both in text and Excel
                for pm in payload["power_modules"]:
                    temp_values.append(pm["ambient_temperature"] / 10.0) # Temperature in Celsius
                    current_values.append(pm["current"])  # Current in Amps
                    voltage_values.append(pm["voltage"])  # Voltage in Volts

                data = {}
                data = {
                    "soc": soc,
                    "soh": soh,
                    "temp": temp_values,
                    "current": current_values,
                    "voltage": voltage_values,
                }
                print(data)
                queue.put(data)

                # print(f"  Module Status Flag 2: {pm['module_status_flag_2'].hex()} ({int(pm['module_status_flag_2'].hex(), 16)})")
                # # logger.log_message(f"  Module Status Flag 2: {pm['module_status_flag_2'].hex()} ({int(pm['module_status_flag_2'].hex(), 16)})")
                # # logger.log_message_txt(f"  Module Status Flag 2: {pm['module_status_flag_2'].hex()} ({int(pm['module_status_flag_2'].hex(), 16)})")

                # print(f"  Ambient Temperature: {pm['ambient_temperature_hex']} ({pm['ambient_temperature']}) (°C)")
                # # logger.log_message(f"  Ambient Temperature: {pm['ambient_temperature_hex']} ({pm['ambient_temperature']}) (°C)")
                # # logger.log_message_txt(f"  Ambient Temperature: {pm['ambient_temperature_hex']} ({pm['ambient_temperature']}) (°C)")

                # print(f"  Current (MSB to LSB): {pm['current_hex']} ({pm['current']}) (A)")
                # # logger.log_message(f"  Current (MSB to LSB): {pm['current_hex']} ({pm['current']}) (A)")
                # # logger.log_message_txt(f"  Current (MSB to LSB): {pm['current_hex']} ({pm['current']}) (A)")

                # print(f"  Voltage (MSB to LSB): {pm['voltage_hex']} ({pm['voltage']}) (V)")
                # # logger.log_message(f"  Voltage (MSB to LSB): {pm['voltage_hex']} ({pm['voltage']}) (V)")
                # # logger.log_message_txt(f"  Voltage (MSB to LSB): {pm['voltage_hex']} ({pm['voltage']}) (V)")

                # print(f"  Reserved: {pm['reserved'].hex()}")
                # # logger.log_message(f"  Reserved: {pm['reserved'].hex()}")
                # # logger.log_message_txt(f"  Reserved: {pm['reserved'].hex()}")

                # update_ui(soc, soh, temperature, current, voltage)

                # Charging Related Info Logging

                # print(f"  Reserved_1: {charging_info['reserved_1'].hex()}")
                # # logger.log_message(f"  Reserved_1: {charging_info['reserved_1'].hex()}")
                # # logger.log_message_txt(f"  Reserved_1: {charging_info['reserved_1'].hex()}")

                # print(f"  Reserved High Nibble: {charging_info['reserved_high_nibble']:X}")
                # # logger.log_message(f"  Reserved High Nibble: {charging_info['reserved_high_nibble']:X}")
                # # logger.log_message_txt(f"  Reserved High Nibble: {charging_info['reserved_high_nibble']:X}")

                # print(f"  Charge Enable Bit: {charging_info['charge_enable_bit']}")
                # # logger.log_message(f"  Charge Enable Bit: {charging_info['charge_enable_bit']}")
                # # logger.log_message_txt(f"  Charge Enable Bit: {charging_info['charge_enable_bit']}")

                # print(f"  Reserved Low Bits: {charging_info['reserved_low_bits']:03b}")
                # # logger.log_message(f"  Reserved Low Bits: {charging_info['reserved_low_bits']:03b}")
                # # logger.log_message_txt(f"  Reserved Low Bits: {charging_info['reserved_low_bits']:03b}")

                # print(f"  Charging state count (Hex): {charging_info['charging_state_count'].hex()}")
                # # logger.log_message(f"  Charging state count (Hex): {charging_info['charging_state_count'].hex()}")
                # # logger.log_message_txt(f"  Charging state count (Hex): {charging_info['charging_state_count'].hex()}")

                # print(f"  Charging State: {charging_info['charging_state']} (decimal)")
                # # logger.log_message(f"  Charging State: {charging_info['charging_state']} (decimal)")
                # # logger.log_message_txt(f"  Charging State: {charging_info['charging_state']} (decimal)")

                # print(f"  Contactor Status: {charging_info['contactor_status']} (bitwise)")
                # # logger.log_message(f"  Contactor Status: {charging_info['contactor_status']} (bitwise)")
                # # logger.log_message_txt(f"  Contactor Status: {charging_info['contactor_status']} (bitwise)")

                # print(f"  Demand Voltage (MSB to LSB): {charging_info['demand_voltage_hex']} ({charging_info['demand_voltage']}) (V)")
                # # logger.log_message(f"  Demand Voltage (MSB to LSB): {charging_info['demand_voltage_hex']} ({charging_info['demand_voltage']}) (V)")
                # # logger.log_message_txt(f"  Demand Voltage (MSB to LSB): {charging_info['demand_voltage_hex']} ({charging_info['demand_voltage']}) (V)")

                # print(f"  Demand Current (MSB to LSB): {charging_info['demand_current_hex']} ({charging_info['demand_current']}) (A)")
                # # logger.log_message(f"  Demand Current (MSB to LSB): {charging_info['demand_current_hex']} ({charging_info['demand_current']}) (A)")
                # # logger.log_message_txt(f"  Demand Current (MSB to LSB): {charging_info['demand_current_hex']} ({charging_info['demand_current']}) (A)")

                # print(f"  Positive Gun Temperature: {charging_info['positive_gun_temperature'].hex()} ({int(charging_info['positive_gun_temperature'].hex(), 16)})")
                # # logger.log_message(f"  Positive Gun Temperature: {charging_info['positive_gun_temperature'].hex()} ({int(charging_info['positive_gun_temperature'].hex(), 16)})")
                # # logger.log_message_txt(f"  Positive Gun Temperature: {charging_info['positive_gun_temperature'].hex()} ({int(charging_info['positive_gun_temperature'].hex(), 16)})")

                # print(f"  Negative Gun Temperature: {charging_info['negative_gun_temperature'].hex()} ({int(charging_info['negative_gun_temperature'].hex(), 16)})")
                # # logger.log_message(f"  Negative Gun Temperature: {charging_info['negative_gun_temperature'].hex()} ({int(charging_info['negative_gun_temperature'].hex(), 16)})")
                # # logger.log_message_txt(f"  Negative Gun Temperature: {charging_info['negative_gun_temperature'].hex()} ({int(charging_info['negative_gun_temperature'].hex(), 16)})")

                # print(f"  Reserved_2: {charging_info['reserved_2'].hex()}")
                # # logger.log_message(f"  Reserved_2: {charging_info['reserved_2'].hex()}")
                # # logger.log_message_txt(f"  Reserved_2: {charging_info['reserved_2'].hex()}")

                # print(f"  Charging Current (MSB to LSB): {charging_info['charging_current_hex']} ({charging_info['charging_current']}) (A)")
                # # logger.log_message(f"  Charging Current (MSB to LSB): {charging_info['charging_current_hex']} ({charging_info['charging_current']}) (A)")
                # # logger.log_message_txt(f"  Charging Current (MSB to LSB): {charging_info['charging_current_hex']} ({charging_info['charging_current']}) (A)")

                # print(f"  Charging Voltage (MSB to LSB): {charging_info['charging_voltage_hex']} ({charging_info['charging_voltage']}) (V)")
                # # logger.log_message(f"  Charging Voltage (MSB to LSB): {charging_info['charging_voltage_hex']} ({charging_info['charging_voltage']}) (V)")
                # # logger.log_message_txt(f"  Charging Voltage (MSB to LSB): {charging_info['charging_voltage_hex']} ({charging_info['charging_voltage']}) (V)")

                # print(f"  Charging Time (Minute): {charging_info['charging_time_minute'].hex()} ({int(charging_info['charging_time_minute'].hex(), 16)})")
                # # logger.log_message(f"  Charging Time (Minute): {charging_info['charging_time_minute'].hex()} ({int(charging_info['charging_time_minute'].hex(), 16)})")
                # # logger.log_message_txt(f"  Charging Time (Minute): {charging_info['charging_time_minute'].hex()} ({int(charging_info['charging_time_minute'].hex(), 16)})")

                # print(f"  Charging Time (Hour): {charging_info['charging_time_hour'].hex()} ({int(charging_info['charging_time_hour'].hex(), 16)})")
                # # logger.log_message(f"  Charging Time (Hour): {charging_info['charging_time_hour'].hex()} ({int(charging_info['charging_time_hour'].hex(), 16)})")
                # # logger.log_message_txt(f"  Charging Time (Hour): {charging_info['charging_time_hour'].hex()} ({int(charging_info['charging_time_hour'].hex(), 16)})")

                # print(f"  Reserved_3: {charging_info['reserved_3'].hex()}")
                # # logger.log_message(f"  Reserved_3: {charging_info['reserved_3'].hex()}")
                # # logger.log_message_txt(f"  Reserved_3: {charging_info['reserved_3'].hex()}")

                # print(f"  BST Reason: {charging_info['BST_reason'].hex()} ({int(charging_info['BST_reason'].hex(), 16)})")
                # # logger.log_message(f"  BST Reason: {charging_info['BST_reason'].hex()} ({int(charging_info['BST_reason'].hex(), 16)})")
                # # logger.log_message_txt(f"  BST Reason: {charging_info['BST_reason'].hex()} ({int(charging_info['BST_reason'].hex(), 16)})")

                # print(f"  CST Reason: {charging_info['CST_reason'].hex()} ({int(charging_info['CST_reason'].hex(), 16)})")
                # # logger.log_message(f"  CST Reason: {charging_info['CST_reason'].hex()} ({int(charging_info['CST_reason'].hex(), 16)})")
                # # logger.log_message_txt(f"  CST Reason: {charging_info['CST_reason'].hex()} ({int(charging_info['CST_reason'].hex(), 16)})")

                # print(f"  Energy Data: {charging_info['energy_data'].hex()} ({int(charging_info['energy_data'].hex(), 16)})")
                # # logger.log_message(f"  Energy Data: {charging_info['energy_data'].hex()} ({int(charging_info['energy_data'].hex(), 16)})")
                # # logger.log_message_txt(f"  Energy Data: {charging_info['energy_data'].hex()} ({int(charging_info['energy_data'].hex(), 16)})")

                # # Print Padding
                # print(f"Padding: {payload['padding'].hex()}")
                # # logger.log_message(f"Padding: {payload['padding'].hex()}")
                # # logger.log_message_txt(f"Padding: {payload['padding'].hex()}")

                # # Print CRC
                # print(f"CRC1: {payload['CRC1'].hex()}")
                # # logger.log_message(f"CRC1: {payload['CRC1'].hex()}")
                # # logger.log_message_txt(f"CRC1: {payload['CRC1'].hex()}")

                # print(f"CRC2: {payload['CRC2'].hex()}")
                # # logger.log_message(f"CRC2: {payload['CRC2'].hex()}")
                # # logger.log_message_txt(f"CRC2: {payload['CRC2'].hex()}")
            except Exception as e:
                print(f"Error: {e}")
                # logger.log_message(f"Error: {e}")
                # logger.log_message_txt(f"Error: {e}")
        else:
            print(f"Expected {TOTAL_SIZE} bytes but received {len(data)} bytes")
            # logger.log_message(f"Expected {TOTAL_SIZE} bytes but received {len(data)} bytes")
            # logger.log_message_txt(f"Expected {TOTAL_SIZE} bytes but received {len(data)} bytes")


# except Exception as e:
#     print(f"Failed to connect to server {server_ip}:{server_port}. Error: {e}")
# logger.log_message(f"Failed to connect to server {server_ip}:{server_port}. Error: {e}")
# logger.log_message_txt(f"Failed to connect to server {server_ip}:{server_port}. Error: {e}")
# finally:
#     client_socket.close()
