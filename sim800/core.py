import machine
import utime

class SIM800:
    """
    Core class for handling communication with the SIM800 module.
    Includes basic functionalities to initialize, send commands, and read responses.
    """
    def __init__(self, uart_pin, baud=115200):
        """
        Initializes the UART connection with the SIM800 module.
        """
        self.uart = machine.UART(uart_pin, baudrate=baud)
        self.initialize()

    def send_command(self, command, timeout=1000):
        """
        Sends an AT command to the SIM800 module.
        """
        self.uart.write(command + '\r')
        utime.sleep_ms(100)  # Delay to allow command processing
        return self.read_response(timeout)

    def read_response(self, timeout=1000):
        """
        Reads the response from the SIM800 module over UART.
        """
        start_time = utime.ticks_ms()
        response = b''
        while (utime.ticks_diff(utime.ticks_ms(), start_time) < timeout):
            if self.uart.any():
                response += self.uart.read(self.uart.any())
        return response

    def initialize(self):
        """
        Basic initialization commands to set up the SIM800 module.
        """
        self.send_command('AT')  # Check module presence
        self.send_command('ATE0')  # Turn off command echoing
        self.send_command('AT+CFUN=1')  # Set full functionality mode

    def reset(self):
        """
        Resets the SIM800 module.
        """
        self.send_command('AT+CFUN=1,1')  # Reset the module

    def get_network_time(self):
        """
        Gets the current time from the network.
        Returns a dictionary with year, month, day, hour, minute, second, and timezone,
        or None if the time could not be retrieved.
        """
        response = self.send_command('AT+CCLK?')
        response_str = response.decode('utf-8') if isinstance(response, bytes) else response

        if '+CCLK:' in response_str:
            try:
                # Response format: +CCLK: "yy/MM/dd,HH:mm:ss±zz"
                time_str = response_str.split('+CCLK:')[1].split('"')[1]
                date_part, time_part = time_str.split(',')
                year, month, day = date_part.split('/')

       
                if '+' in time_part:
                    time_only, tz = time_part.split('+')
                    tz = '+' + tz
                elif '-' in time_part[2:]:  
                    idx = time_part.rfind('-')
                    time_only = time_part[:idx]
                    tz = time_part[idx:]
                else:
                    time_only = time_part
                    tz = '+00'

                hour, minute, second = time_only.split(':')

                return {
                    'year': int(year) + 2000,
                    'month': int(month),
                    'day': int(day),
                    'hour': int(hour),
                    'minute': int(minute),
                    'second': int(second),
                    'timezone': tz
                }
            except (IndexError, ValueError):
                return None
        return None

