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
