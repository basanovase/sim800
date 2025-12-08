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

    def start_udp_connection(self, ip, port):
        """
        Start a UDP connection to the specified IP address and port.

        :param ip: The remote IP address to connect to.
        :param port: The remote port number.
        :return: The response from the SIM800 module.
        """
        return self.send_command(f'AT+CIPSTART="UDP","{ip}","{port}"')

    def send_data_udp(self, data):
        """
        Send data through the UDP connection.

        :param data: The data to send (string or bytes).
        :return: The response from the SIM800 module.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.send_command(f'AT+CIPSEND={len(data)}')
        self.uart.write(data + bytes([26]))  # End with Ctrl-Z
        return self.read_response()

    def receive_data_udp(self, max_length=1460):
        """
        Receive data from UDP connection.

        :param max_length: Maximum number of bytes to receive (default 1460, typical MTU).
        :return: The response containing received data.
        """
        return self.send_command(f'AT+CIPRXGET=2,{max_length}')

    def close_udp_connection(self):
        """
        Close the UDP connection.

        :return: The response from the SIM800 module.
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

    def http_terminate(self):
        """
        Terminate HTTP service and release resources.

        :return: The response from the SIM800 module.
        """
        return self.send_command('AT+HTTPTERM')

    def ftp_init(self, server, username, password, port=21):
        """
        Initialize FTP session with server credentials.

        :param server: FTP server address.
        :param username: FTP username.
        :param password: FTP password.
        :param port: FTP port (default 21).
        :return: The response from the SIM800 module.
        """
        self.send_command('AT+SAPBR=3,1,"Contype","GPRS"')
        self.send_command('AT+SAPBR=1,1')
        self.send_command(f'AT+FTPCID=1')
        self.send_command(f'AT+FTPSERV="{server}"')
        self.send_command(f'AT+FTPPORT={port}')
        self.send_command(f'AT+FTPUN="{username}"')
        return self.send_command(f'AT+FTPPW="{password}"')

    def ftp_get_file(self, filename, remote_path):
        """
        Download a file from the FTP server.

        :param filename: The name of the file to download.
        :param remote_path: The remote directory path where the file is located.
        :return: The file content from the FTP server.
        """
        self.send_command(f'AT+FTPGETPATH="{remote_path}"')
        self.send_command(f'AT+FTPGETNAME="{filename}"')
        self.send_command('AT+FTPGET=1')
        return self.send_command('AT+FTPGET=2,1024', timeout=10000)

    def ftp_put_file(self, filename, remote_path, data):
        """
        Upload a file to the FTP server.

        :param filename: The name of the file to upload.
        :param remote_path: The remote directory path to upload to.
        :param data: The file content to upload.
        :return: The response from the SIM800 module.
        """
        self.send_command(f'AT+FTPPUTPATH="{remote_path}"')
        self.send_command(f'AT+FTPPUTNAME="{filename}"')
        self.send_command('AT+FTPPUT=1')
        self.send_command(f'AT+FTPPUT=2,{len(data)}')
        self.uart.write(data if isinstance(data, bytes) else data.encode('utf-8'))
        return self.read_response()

    def ftp_close(self):
        """
        Close the FTP session and release bearer.

        :return: The response from the SIM800 module.
        """
        return self.send_command('AT+SAPBR=0,1')
