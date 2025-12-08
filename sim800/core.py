import machine
import utime

from .exceptions import (
    SIM800CommandError,
    SIM800TimeoutError,
    SIM800InitializationError,
)

# Default retry configuration
DEFAULT_RETRIES = 3
DEFAULT_RETRY_DELAY_MS = 500


class SIM800:
    """
    Core class for handling communication with the SIM800 module.
    Includes basic functionalities to initialize, send commands, and read responses.
    """

    def __init__(self, uart_pin, baud=115200, retries=DEFAULT_RETRIES, retry_delay_ms=DEFAULT_RETRY_DELAY_MS):
        """
        Initializes the UART connection with the SIM800 module.

        :param uart_pin: The UART pin number to use.
        :param baud: Baud rate for UART communication (default 115200).
        :param retries: Default number of retries for commands (default 3).
        :param retry_delay_ms: Delay between retries in milliseconds (default 500).
        :raises SIM800InitializationError: If module initialization fails.
        """
        self.retries = retries
        self.retry_delay_ms = retry_delay_ms
        try:
            self.uart = machine.UART(uart_pin, baudrate=baud)
        except Exception as e:
            raise SIM800InitializationError("Failed to initialize UART: {}".format(e))
        self.initialize()

    def send_command(self, command, timeout=1000, check_error=True):
        """
        Sends an AT command to the SIM800 module.

        :param command: The AT command to send.
        :param timeout: Timeout in milliseconds to wait for response.
        :param check_error: If True, raises exception on ERROR response.
        :return: The response from the module.
        :raises SIM800CommandError: If the command returns an ERROR response.
        :raises SIM800TimeoutError: If no response is received within timeout.
        """
        self.uart.write(command + '\r')
        utime.sleep_ms(100)  # Delay to allow command processing
        response = self.read_response(timeout)

        if check_error and response:
            response_str = self._decode_response(response)
            if 'ERROR' in response_str:
                raise SIM800CommandError(command, response_str.strip())

        return response

    def send_command_with_retry(self, command, timeout=1000, check_error=True,
                                 retries=None, retry_delay_ms=None):
        """
        Sends an AT command with automatic retry on failure.

        Useful for commands that may fail due to transient cellular network issues.

        :param command: The AT command to send.
        :param timeout: Timeout in milliseconds to wait for response.
        :param check_error: If True, raises exception on ERROR response.
        :param retries: Number of retry attempts (uses instance default if None).
        :param retry_delay_ms: Delay between retries in ms (uses instance default if None).
        :return: The response from the module.
        :raises SIM800CommandError: If all retries fail with ERROR response.
        :raises SIM800TimeoutError: If all retries timeout.
        """
        if retries is None:
            retries = self.retries
        if retry_delay_ms is None:
            retry_delay_ms = self.retry_delay_ms

        last_exception = None

        for attempt in range(retries + 1):
            try:
                return self.send_command(command, timeout, check_error)
            except (SIM800CommandError, SIM800TimeoutError) as e:
                last_exception = e
                if attempt < retries:
                    utime.sleep_ms(retry_delay_ms)
                    # Clear any pending data in UART buffer before retry
                    self._clear_uart_buffer()

        # All retries exhausted
        raise last_exception

    def _clear_uart_buffer(self):
        """
        Clear any pending data in the UART receive buffer.
        """
        while self.uart.any():
            self.uart.read()

    def read_response(self, timeout=1000):
        """
        Reads the response from the SIM800 module over UART.

        :param timeout: Timeout in milliseconds.
        :return: The response as bytes.
        """
        start_time = utime.ticks_ms()
        response = b''
        while (utime.ticks_diff(utime.ticks_ms(), start_time) < timeout):
            if self.uart.any():
                response += self.uart.read(self.uart.any())
        return response

    def _decode_response(self, response):
        """
        Decode response bytes to string safely.

        :param response: Response as bytes or string.
        :return: Response as string.
        """
        if isinstance(response, bytes):
            try:
                return response.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback: decode byte by byte, replacing invalid chars
                result = ''
                for b in response:
                    if b < 128:
                        result += chr(b)
                    else:
                        result += '?'
                return result
        return response

    def _check_response_ok(self, response, command):
        """
        Check if response contains OK.

        :param response: The response to check.
        :param command: The command that was sent (for error messages).
        :raises SIM800CommandError: If response doesn't contain OK.
        """
        response_str = self._decode_response(response)
        if 'OK' not in response_str:
            raise SIM800CommandError(command, response_str.strip())

    def initialize(self):
        """
        Basic initialization commands to set up the SIM800 module.

        :raises SIM800InitializationError: If any initialization command fails.
        """
        try:
            # Check module presence with retries (module may be slow to start)
            response = None
            for attempt in range(self.retries + 1):
                response = self.send_command('AT', check_error=False)
                response_str = self._decode_response(response)
                if 'OK' in response_str or 'AT' in response_str:
                    break
                if attempt < self.retries:
                    utime.sleep_ms(self.retry_delay_ms)
            else:
                raise SIM800InitializationError("Module not responding to AT command")

            # Turn off command echoing
            self.send_command('ATE0')

            # Set full functionality mode
            self.send_command('AT+CFUN=1')

        except SIM800CommandError as e:
            raise SIM800InitializationError("Initialization failed: {}".format(e))

    def reset(self):
        """
        Resets the SIM800 module.

        :raises SIM800CommandError: If reset command fails.
        """
        self.send_command('AT+CFUN=1,1')

    def dial_number(self, number):
        """
        Initiate a voice call to the specified phone number.

        :param number: The phone number to dial (e.g., '+1234567890').
        :return: The response from the SIM800 module.
        :raises ValueError: If phone number is empty.
        :raises SIM800CommandError: If dial command fails.
        """
        if not number:
            raise ValueError("Phone number cannot be empty")
        return self.send_command('ATD{};'.format(number))

    def hang_up(self):
        """
        Hang up the current voice call.

        :return: The response from the SIM800 module.
        :raises SIM800CommandError: If hang up command fails.
        """
        return self.send_command('ATH')

    def get_network_time(self):
        """
        Gets the current time from the network.

        :return: Dictionary with year, month, day, hour, minute, second, and timezone,
                 or None if the time could not be retrieved.
        """
        try:
            response = self.send_command('AT+CCLK?', check_error=False)
        except SIM800CommandError:
            return None

        response_str = self._decode_response(response)

        if '+CCLK:' in response_str:
            try:
                # Response format: +CCLK: "yy/MM/dd,HH:mm:ss±zz"
                time_str = response_str.split('+CCLK:')[1].split('"')[1]
                date_part, time_part = time_str.split(',')
                year, month, day = date_part.split('/')

                # Handle timezone offset in time part (e.g., "12:30:45+04")
                if '+' in time_part:
                    time_only, tz = time_part.split('+')
                    tz = '+' + tz
                elif '-' in time_part[2:]:  # Skip first char to avoid negative hour confusion
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
