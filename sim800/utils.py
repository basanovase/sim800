import utime

class SIM800Utils:
    @staticmethod
    def wait_for_response(uart, expected_response, timeout=5000):
        """
        Waits for a specific response from the SIM800 module.

        :param uart: The UART object used for communication.
        :param expected_response: The response string to wait for.
        :param timeout: The maximum time to wait in milliseconds.
        :return: The response if received, or None if timeout occurs.
        """
        start_time = utime.ticks_ms()
        response = b''

        while utime.ticks_diff(utime.ticks_ms(), start_time) < timeout:
            if uart.any():
                response += uart.read(uart.any())
                if expected_response.encode() in response:
                    return response.decode('utf-8')
            utime.sleep_ms(100)

        return None

    @staticmethod
    def clear_uart_buffer(uart):
        """
        Clears the UART buffer to avoid leftover data affecting new commands.

        :param uart: The UART object whose buffer is to be cleared.
        """
        while uart.any():
            uart.read()

    @staticmethod
    def send_command(uart, command, wait_for="OK", timeout=2000):
        """
        Sends an AT command to the SIM800 module and waits for a response.

        :param uart: The UART object used for communication.
        :param command: The AT command to send.
        :param wait_for: The expected response to wait for.
        :param timeout: The maximum time to wait for the response in milliseconds.
        :return: The response from the SIM800 module, or None if timeout occurs.
        """
        SIM800Utils.clear_uart_buffer(uart)
        uart.write(command + '\r')
        return SIM800Utils.wait_for_response(uart, wait_for, timeout)


        # ensure the message is properly encoded (e.g., GSM 7-bit).
        return message  # Assuming no encoding is necessary in this example.
