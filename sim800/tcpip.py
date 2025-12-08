from .core import SIM800
from .exceptions import (
    SIM800ConnectionError,
    SIM800CommandError,
    SIM800HTTPError,
    SIM800FTPError,
)


class SIM800TCPIP(SIM800):

    def _validate_port(self, port):
        """
        Validate port number.

        :param port: Port number to validate.
        :raises ValueError: If port is invalid.
        """
        try:
            port_int = int(port)
            if not (1 <= port_int <= 65535):
                raise ValueError("Port must be between 1 and 65535, got {}".format(port))
        except (TypeError, ValueError):
            raise ValueError("Invalid port: {}".format(port))

    def _validate_ip_or_host(self, ip):
        """
        Validate IP address or hostname is not empty.

        :param ip: IP address or hostname to validate.
        :raises ValueError: If IP/hostname is empty.
        """
        if not ip or not str(ip).strip():
            raise ValueError("IP address or hostname cannot be empty")

    def start_tcp_connection(self, mode, ip, port, retry=True):
        """
        Start a TCP or UDP connection.

        :param mode: Connection mode ('TCP' or 'UDP').
        :param ip: IP address or hostname to connect to.
        :param port: Port number to connect to.
        :param retry: If True, retry connection on failure (default True).
        :return: The response from the SIM800 module.
        :raises ValueError: If mode, ip, or port is invalid.
        :raises SIM800ConnectionError: If connection fails.
        """
        mode = str(mode).upper()
        if mode not in ('TCP', 'UDP'):
            raise ValueError("Mode must be 'TCP' or 'UDP', got '{}'".format(mode))
        self._validate_ip_or_host(ip)
        self._validate_port(port)

        command = 'AT+CIPSTART="{}","{}","{}"'.format(mode, ip, port)
        last_error = None

        attempts = (self.retries + 1) if retry else 1
        for attempt in range(attempts):
            try:
                response = self.send_command(command, timeout=10000)
                response_str = self._decode_response(response)
                if 'CONNECT OK' in response_str or 'ALREADY CONNECT' in response_str:
                    return response
                if 'CONNECT FAIL' in response_str:
                    last_error = SIM800ConnectionError("Failed to connect to {}:{}".format(ip, port), ip, port)
                else:
                    return response
            except SIM800CommandError as e:
                last_error = SIM800ConnectionError("Connection failed: {}".format(e), ip, port)

            # Retry after delay if not last attempt
            if attempt < attempts - 1:
                import utime
                utime.sleep_ms(self.retry_delay_ms)

        raise last_error

    def send_data_tcp(self, data):
        """
        Send data through the TCP or UDP connection.

        :param data: Data to send (string or bytes).
        :return: The response from the SIM800 module.
        :raises SIM800CommandError: If send fails.
        """
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        self.send_command('AT+CIPSEND={}'.format(len(data_bytes)), check_error=False)
        self.uart.write(data_bytes + bytes([26]))  # End with Ctrl-Z
        return self.read_response()

    def receive_data_tcp(self):
        """
        Receive data from TCP or UDP connection.

        :return: The response containing received data.
        :raises SIM800CommandError: If receive fails.
        """
        return self.send_command('AT+CIPRXGET=2')

    def close_tcp_connection(self):
        """
        Close the TCP or UDP connection.

        :return: The response from the SIM800 module.
        :raises SIM800CommandError: If close fails.
        """
        return self.send_command('AT+CIPCLOSE=1', check_error=False)

    def start_udp_connection(self, ip, port, retry=True):
        """
        Start a UDP connection to the specified IP address and port.

        :param ip: The remote IP address to connect to.
        :param port: The remote port number.
        :param retry: If True, retry connection on failure (default True).
        :return: The response from the SIM800 module.
        :raises ValueError: If ip or port is invalid.
        :raises SIM800ConnectionError: If connection fails.
        """
        self._validate_ip_or_host(ip)
        self._validate_port(port)

        command = 'AT+CIPSTART="UDP","{}","{}"'.format(ip, port)
        last_error = None

        attempts = (self.retries + 1) if retry else 1
        for attempt in range(attempts):
            try:
                response = self.send_command(command, timeout=10000)
                response_str = self._decode_response(response)
                if 'CONNECT OK' in response_str or 'ALREADY CONNECT' in response_str:
                    return response
                if 'CONNECT FAIL' in response_str:
                    last_error = SIM800ConnectionError("Failed to connect to {}:{}".format(ip, port), ip, port)
                else:
                    return response
            except SIM800CommandError as e:
                last_error = SIM800ConnectionError("UDP connection failed: {}".format(e), ip, port)

            # Retry after delay if not last attempt
            if attempt < attempts - 1:
                import utime
                utime.sleep_ms(self.retry_delay_ms)

        raise last_error

    def send_data_udp(self, data):
        """
        Send data through the UDP connection.

        :param data: The data to send (string or bytes).
        :return: The response from the SIM800 module.
        :raises SIM800CommandError: If send fails.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.send_command('AT+CIPSEND={}'.format(len(data)), check_error=False)
        self.uart.write(data + bytes([26]))  # End with Ctrl-Z
        return self.read_response()

    def receive_data_udp(self, max_length=1460):
        """
        Receive data from UDP connection.

        :param max_length: Maximum number of bytes to receive (default 1460, typical MTU).
        :return: The response containing received data.
        :raises ValueError: If max_length is invalid.
        :raises SIM800CommandError: If receive fails.
        """
        if not isinstance(max_length, int) or max_length <= 0:
            raise ValueError("max_length must be a positive integer, got {}".format(max_length))
        return self.send_command('AT+CIPRXGET=2,{}'.format(max_length))

    def close_udp_connection(self):
        """
        Close the UDP connection.

        :return: The response from the SIM800 module.
        :raises SIM800CommandError: If close fails.
        """
        return self.send_command('AT+CIPCLOSE=1', check_error=False)

    def shutdown_gprs(self):
        """
        Deactivate GPRS PDP context, effectively shutting down the GPRS service.

        :return: The response from the SIM800 module.
        :raises SIM800CommandError: If shutdown fails.
        """
        return self.send_command('AT+CIPSHUT')

    def get_ip_address(self):
        """
        Get local IP address.

        :return: The response containing the local IP address.
        :raises SIM800CommandError: If command fails.
        """
        return self.send_command('AT+CIFSR', check_error=False)

    def http_init(self):
        """
        Initialize HTTP service.

        :return: The response from the SIM800 module.
        :raises SIM800HTTPError: If HTTP initialization fails.
        """
        try:
            return self.send_command('AT+HTTPINIT')
        except SIM800CommandError as e:
            raise SIM800HTTPError("Failed to initialize HTTP: {}".format(e))

    def http_set_param(self, param, value):
        """
        Set HTTP parameter.

        :param param: Parameter name (e.g., 'URL', 'CONTENT', 'UA').
        :param value: Parameter value.
        :return: The response from the SIM800 module.
        :raises ValueError: If param or value is empty.
        :raises SIM800HTTPError: If setting parameter fails.
        """
        if not param:
            raise ValueError("Parameter name cannot be empty")
        try:
            return self.send_command('AT+HTTPPARA="{}","{}"'.format(param, value))
        except SIM800CommandError as e:
            raise SIM800HTTPError("Failed to set HTTP parameter '{}': {}".format(param, e))

    def http_get(self, url):
        """
        Perform HTTP GET method.

        :param url: The URL to request.
        :return: The response from the server.
        :raises ValueError: If URL is empty.
        :raises SIM800HTTPError: If HTTP GET fails.
        """
        if not url:
            raise ValueError("URL cannot be empty")
        try:
            self.http_set_param("URL", url)
            self.send_command('AT+HTTPACTION=0', check_error=False)
            return self.read_response()
        except SIM800CommandError as e:
            raise SIM800HTTPError("HTTP GET failed: {}".format(e), url=url)

    def http_post(self, url, data):
        """
        Perform HTTP POST method.

        :param url: The URL to post to.
        :param data: The data to post.
        :return: The response from the server.
        :raises ValueError: If URL is empty.
        :raises SIM800HTTPError: If HTTP POST fails.
        """
        if not url:
            raise ValueError("URL cannot be empty")
        try:
            self.http_set_param("URL", url)
            if isinstance(data, str):
                data = data.encode('utf-8')
            self.send_command('AT+HTTPDATA={},10000'.format(len(data)), check_error=False)
            self.uart.write(data)
            self.send_command('AT+HTTPACTION=1', check_error=False)
            return self.read_response()
        except SIM800CommandError as e:
            raise SIM800HTTPError("HTTP POST failed: {}".format(e), url=url)

    def http_terminate(self):
        """
        Terminate HTTP service and release resources.

        :return: The response from the SIM800 module.
        :raises SIM800HTTPError: If termination fails.
        """
        try:
            return self.send_command('AT+HTTPTERM')
        except SIM800CommandError as e:
            raise SIM800HTTPError("Failed to terminate HTTP: {}".format(e))

    def ftp_init(self, server, username, password, port=21):
        """
        Initialize FTP session with server credentials.

        :param server: FTP server address.
        :param username: FTP username.
        :param password: FTP password.
        :param port: FTP port (default 21).
        :return: The response from the SIM800 module.
        :raises ValueError: If server, username, or password is empty.
        :raises SIM800FTPError: If FTP initialization fails.
        """
        if not server:
            raise ValueError("FTP server cannot be empty")
        if not username:
            raise ValueError("FTP username cannot be empty")
        if not password:
            raise ValueError("FTP password cannot be empty")
        self._validate_port(port)

        try:
            self.send_command('AT+SAPBR=3,1,"Contype","GPRS"')
            self.send_command('AT+SAPBR=1,1', check_error=False)  # May already be open
            self.send_command('AT+FTPCID=1')
            self.send_command('AT+FTPSERV="{}"'.format(server))
            self.send_command('AT+FTPPORT={}'.format(port))
            self.send_command('AT+FTPUN="{}"'.format(username))
            return self.send_command('AT+FTPPW="{}"'.format(password))
        except SIM800CommandError as e:
            raise SIM800FTPError("FTP initialization failed: {}".format(e))

    def ftp_get_file(self, filename, remote_path):
        """
        Download a file from the FTP server.

        :param filename: The name of the file to download.
        :param remote_path: The remote directory path where the file is located.
        :return: The file content from the FTP server.
        :raises ValueError: If filename or remote_path is empty.
        :raises SIM800FTPError: If file download fails.
        """
        if not filename:
            raise ValueError("Filename cannot be empty")
        if not remote_path:
            raise ValueError("Remote path cannot be empty")

        try:
            self.send_command('AT+FTPGETPATH="{}"'.format(remote_path))
            self.send_command('AT+FTPGETNAME="{}"'.format(filename))
            self.send_command('AT+FTPGET=1', check_error=False)
            return self.send_command('AT+FTPGET=2,1024', timeout=10000, check_error=False)
        except SIM800CommandError as e:
            raise SIM800FTPError("FTP download failed: {}".format(e), filename=filename, path=remote_path)

    def ftp_put_file(self, filename, remote_path, data):
        """
        Upload a file to the FTP server.

        :param filename: The name of the file to upload.
        :param remote_path: The remote directory path to upload to.
        :param data: The file content to upload.
        :return: The response from the SIM800 module.
        :raises ValueError: If filename, remote_path, or data is empty.
        :raises SIM800FTPError: If file upload fails.
        """
        if not filename:
            raise ValueError("Filename cannot be empty")
        if not remote_path:
            raise ValueError("Remote path cannot be empty")
        if data is None:
            raise ValueError("Data cannot be None")

        try:
            self.send_command('AT+FTPPUTPATH="{}"'.format(remote_path))
            self.send_command('AT+FTPPUTNAME="{}"'.format(filename))
            self.send_command('AT+FTPPUT=1', check_error=False)
            data_bytes = data if isinstance(data, bytes) else data.encode('utf-8')
            self.send_command('AT+FTPPUT=2,{}'.format(len(data_bytes)), check_error=False)
            self.uart.write(data_bytes)
            return self.read_response()
        except SIM800CommandError as e:
            raise SIM800FTPError("FTP upload failed: {}".format(e), filename=filename, path=remote_path)

    def ftp_close(self):
        """
        Close the FTP session and release bearer.

        :return: The response from the SIM800 module.
        :raises SIM800FTPError: If closing FTP session fails.
        """
        try:
            return self.send_command('AT+SAPBR=0,1')
        except SIM800CommandError as e:
            raise SIM800FTPError("Failed to close FTP session: {}".format(e))
