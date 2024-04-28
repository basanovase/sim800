from .core import SIM800

class SIM800GPRS(SIM800):
    def attach_gprs(self):
        """
        Attach to the GPRS service.
        """
        return self.send_command('AT+CGATT=1')

    def detach_gprs(self):
        """
        Detach from the GPRS service.
        """
        return self.send_command('AT+CGATT=0')

    def set_apn(self, apn, user='', pwd=''):
        """
        Set the APN, username, and password for the GPRS connection.
        """
        self.send_command(f'AT+CSTT="{apn}","{user}","{pwd}"')
        return self.send_command('AT+CIICR')

    def get_ip_address(self):
        """
        Get the local IP address assigned to the module.
        """
        return self.send_command('AT+CIFSR')

    def start_tcp_connection(self, mode, ip, port):
        """
        Start a TCP or UDP connection.
        """
        return self.send_command(f'AT+CIPSTART="{mode}","{ip}","{port}"')

    def send_data_tcp(self, data):
        """
        Send data through the TCP or UDP connection.
        """
        self.send_command(f'AT+CIPSEND={len(data)}')
        self.uart.write(data + chr(26))
        return self.read_response()

    def close_tcp_connection(self):
        """
        Close the TCP or UDP connection.
        """
        return self.send_command('AT+CIPCLOSE=1')

    def shutdown_gprs(self):
        """
        Deactivate GPRS PDP context, effectively shutting down the GPRS service.
        """
        return self.send_command('AT+CIPSHUT')
