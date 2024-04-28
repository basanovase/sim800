from .core import SIM800

class SIM800TCPIP(SIM800):
    def start_tcp_connection(self, mode, ip, port):
        """
        Start a TCP or UDP connection.
        Mode can be 'TCP' or 'UDP'. IP address and port number are required.
        """
        return self.send_command(f'AT+CIPSTART="{mode}","{ip}","{port}"')

    def send_data_tcp(self, data):
        """
        Send data through the TCP or UDP connection.
        """
        self.send_command(f'AT+CIPSEND={len(data)}')
        self.uart.write(data + chr(26))  # End with Ctrl-Z
        return self.read_response()

    def receive_data_tcp(self):
        """
        Receive data from TCP or UDP connection.
        """
        return self.send_command('AT+CIPRXGET=2')

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

    def get_ip_address(self):
        """
        Get local IP address.
        """
        return self.send_command('AT+CIFSR')

    def http_init(self):
        """
        Initialize HTTP service.
        """
        return self.send_command('AT+HTTPINIT')

    def http_set_param(self, param, value):
        """
        Set HTTP parameter.
        """
        return self.send_command(f'AT+HTTPPARA="{param}","{value}"')

    def http_get(self, url):
        """
        Perform HTTP GET method.
        """
        self.http_set_param("URL", url)
        self.send_command('AT+HTTPACTION=0')
        return self.read_response()

    def http_post(self, url, data):
        """
        Perform HTTP POST method.
        """
        self.http_set_param("URL", url)
        self.send_command(f'AT+HTTPDATA={len(data)},10000')
        self.uart.write(data)
        self.send_command('AT+HTTPACTION=1')
        return self.read_response()
