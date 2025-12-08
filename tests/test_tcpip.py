import unittest
from unittest.mock import MagicMock, patch, call, ANY
import sys

# Mock the MicroPython modules before importing SIM800TCPIP
sys.modules['machine'] = MagicMock()
sys.modules['utime'] = MagicMock()

from sim800.tcpip import SIM800TCPIP


class TestUDPSocket(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800TCPIP, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800TCPIP(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim.read_response = MagicMock()
            self.sim._decode_response = lambda x: x.decode() if isinstance(x, bytes) else x
            self.sim._validate_port = SIM800TCPIP._validate_port.__get__(self.sim)
            self.sim._validate_ip_or_host = SIM800TCPIP._validate_ip_or_host.__get__(self.sim)
            self.sim.retries = 3
            self.sim.retry_delay_ms = 500

    def test_start_udp_connection(self):
        """Test starting a UDP connection"""
        self.sim.send_command.return_value = b'CONNECT OK\r\n'

        result = self.sim.start_udp_connection('192.168.1.100', 8080)

        self.sim.send_command.assert_called_once_with('AT+CIPSTART="UDP","192.168.1.100","8080"', timeout=10000)
        self.assertEqual(result, b'CONNECT OK\r\n')

    def test_start_udp_connection_with_domain(self):
        """Test starting a UDP connection with domain name"""
        self.sim.send_command.return_value = b'CONNECT OK\r\n'

        result = self.sim.start_udp_connection('example.com', 53)

        self.sim.send_command.assert_called_once_with('AT+CIPSTART="UDP","example.com","53"', timeout=10000)
        self.assertEqual(result, b'CONNECT OK\r\n')

    def test_send_data_udp_string(self):
        """Test sending string data through UDP"""
        self.sim.read_response.return_value = b'SEND OK\r\n'

        result = self.sim.send_data_udp('Hello UDP')

        self.sim.send_command.assert_called_once_with('AT+CIPSEND=9', check_error=False)
        self.sim.uart.write.assert_called_once_with(b'Hello UDP' + bytes([26]))
        self.assertEqual(result, b'SEND OK\r\n')

    def test_send_data_udp_bytes(self):
        """Test sending bytes data through UDP"""
        self.sim.read_response.return_value = b'SEND OK\r\n'
        test_data = b'\x01\x02\x03\x04'

        result = self.sim.send_data_udp(test_data)

        self.sim.send_command.assert_called_once_with('AT+CIPSEND=4', check_error=False)
        self.sim.uart.write.assert_called_once_with(test_data + bytes([26]))
        self.assertEqual(result, b'SEND OK\r\n')

    def test_send_data_udp_empty(self):
        """Test sending empty data through UDP"""
        self.sim.read_response.return_value = b'SEND OK\r\n'

        result = self.sim.send_data_udp('')

        self.sim.send_command.assert_called_once_with('AT+CIPSEND=0', check_error=False)
        self.sim.uart.write.assert_called_once_with(b'' + bytes([26]))

    def test_receive_data_udp_default_length(self):
        """Test receiving data from UDP with default max length"""
        self.sim.send_command.return_value = b'+CIPRXGET: 2,100\r\nHello from server\r\nOK\r\n'

        result = self.sim.receive_data_udp()

        self.sim.send_command.assert_called_once_with('AT+CIPRXGET=2,1460')
        self.assertEqual(result, b'+CIPRXGET: 2,100\r\nHello from server\r\nOK\r\n')

    def test_receive_data_udp_custom_length(self):
        """Test receiving data from UDP with custom max length"""
        self.sim.send_command.return_value = b'+CIPRXGET: 2,50\r\nData\r\nOK\r\n'

        result = self.sim.receive_data_udp(max_length=512)

        self.sim.send_command.assert_called_once_with('AT+CIPRXGET=2,512')

    def test_close_udp_connection(self):
        """Test closing UDP connection"""
        self.sim.send_command.return_value = b'CLOSE OK\r\n'

        result = self.sim.close_udp_connection()

        self.sim.send_command.assert_called_once_with('AT+CIPCLOSE=1', check_error=False)
        self.assertEqual(result, b'CLOSE OK\r\n')

    def test_udp_connection_error(self):
        """Test handling UDP connection error"""
        self.sim.send_command.return_value = b'ERROR\r\n'

        result = self.sim.start_udp_connection('invalid.host', 9999)

        self.assertEqual(result, b'ERROR\r\n')

    def test_full_udp_session(self):
        """Test a complete UDP session workflow"""
        # Setup responses for each call
        self.sim.send_command.side_effect = [
            b'CONNECT OK\r\n',  # start_udp_connection
            b'> ',              # send_data_udp (AT+CIPSEND)
            b'CLOSE OK\r\n'     # close_udp_connection
        ]
        self.sim.read_response.return_value = b'SEND OK\r\n'

        # Execute full session
        connect_result = self.sim.start_udp_connection('192.168.1.1', 5000)
        send_result = self.sim.send_data_udp('test message')
        close_result = self.sim.close_udp_connection()

        # Verify sequence
        self.assertEqual(connect_result, b'CONNECT OK\r\n')
        self.assertEqual(send_result, b'SEND OK\r\n')
        self.assertEqual(close_result, b'CLOSE OK\r\n')


class TestTCPIPExisting(unittest.TestCase):
    """Test that existing TCP/IP methods still work correctly"""

    def setUp(self):
        with patch.object(SIM800TCPIP, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800TCPIP(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim.read_response = MagicMock()
            self.sim._decode_response = lambda x: x.decode() if isinstance(x, bytes) else x
            self.sim._validate_port = SIM800TCPIP._validate_port.__get__(self.sim)
            self.sim._validate_ip_or_host = SIM800TCPIP._validate_ip_or_host.__get__(self.sim)
            self.sim.retries = 3
            self.sim.retry_delay_ms = 500

    def test_start_tcp_connection(self):
        """Test starting a TCP connection still works"""
        self.sim.send_command.return_value = b'CONNECT OK\r\n'

        result = self.sim.start_tcp_connection('TCP', '192.168.1.1', 80)

        self.sim.send_command.assert_called_once_with('AT+CIPSTART="TCP","192.168.1.1","80"', timeout=10000)

    def test_get_ip_address(self):
        """Test getting IP address"""
        self.sim.send_command.return_value = b'10.0.0.1\r\n'

        result = self.sim.get_ip_address()

        self.sim.send_command.assert_called_once_with('AT+CIFSR', check_error=False)


class TestHTTP(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800TCPIP, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800TCPIP(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim.read_response = MagicMock()

    def test_http_terminate(self):
        """Test terminating HTTP service"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.http_terminate()

        self.sim.send_command.assert_called_once_with('AT+HTTPTERM')
        self.assertEqual(result, b'OK\r\n')


class TestFTP(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800TCPIP, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800TCPIP(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim.read_response = MagicMock()
            self.sim._validate_port = SIM800TCPIP._validate_port.__get__(self.sim)

    def test_ftp_init(self):
        """Test FTP initialization with credentials"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.ftp_init('ftp.example.com', 'user', 'pass')

        calls = self.sim.send_command.call_args_list
        self.assertEqual(calls[0], call('AT+SAPBR=3,1,"Contype","GPRS"'))
        self.assertEqual(calls[1], call('AT+SAPBR=1,1', check_error=False))
        self.assertEqual(calls[2], call('AT+FTPCID=1'))
        self.assertEqual(calls[3], call('AT+FTPSERV="ftp.example.com"'))
        self.assertEqual(calls[4], call('AT+FTPPORT=21'))
        self.assertEqual(calls[5], call('AT+FTPUN="user"'))
        self.assertEqual(calls[6], call('AT+FTPPW="pass"'))

    def test_ftp_init_custom_port(self):
        """Test FTP initialization with custom port"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.ftp_init('ftp.example.com', 'user', 'pass', port=2121)

        calls = self.sim.send_command.call_args_list
        self.assertEqual(calls[4], call('AT+FTPPORT=2121'))

    def test_ftp_get_file(self):
        """Test downloading a file from FTP"""
        self.sim.send_command.side_effect = [
            b'OK\r\n',  # FTPGETPATH
            b'OK\r\n',  # FTPGETNAME
            b'OK\r\n',  # FTPGET=1
            b'+FTPGET: 2,100\r\nfile content here\r\nOK\r\n'  # FTPGET=2
        ]

        result = self.sim.ftp_get_file('file.txt', '/remote/path')

        calls = self.sim.send_command.call_args_list
        self.assertEqual(calls[0], call('AT+FTPGETPATH="/remote/path"'))
        self.assertEqual(calls[1], call('AT+FTPGETNAME="file.txt"'))
        self.assertEqual(calls[2], call('AT+FTPGET=1', check_error=False))
        self.assertEqual(calls[3], call('AT+FTPGET=2,1024', timeout=10000, check_error=False))

    def test_ftp_put_file_string(self):
        """Test uploading string data to FTP"""
        self.sim.send_command.return_value = b'OK\r\n'
        self.sim.read_response.return_value = b'OK\r\n'

        result = self.sim.ftp_put_file('upload.txt', '/remote/', 'file content')

        calls = self.sim.send_command.call_args_list
        self.assertEqual(calls[0], call('AT+FTPPUTPATH="/remote/"'))
        self.assertEqual(calls[1], call('AT+FTPPUTNAME="upload.txt"'))
        self.assertEqual(calls[2], call('AT+FTPPUT=1', check_error=False))
        self.assertEqual(calls[3], call('AT+FTPPUT=2,12', check_error=False))
        self.sim.uart.write.assert_called_once_with(b'file content')

    def test_ftp_put_file_bytes(self):
        """Test uploading bytes data to FTP"""
        self.sim.send_command.return_value = b'OK\r\n'
        self.sim.read_response.return_value = b'OK\r\n'
        test_data = b'\x00\x01\x02\x03'

        result = self.sim.ftp_put_file('binary.dat', '/data/', test_data)

        self.sim.uart.write.assert_called_once_with(test_data)

    def test_ftp_close(self):
        """Test closing FTP session"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.ftp_close()

        self.sim.send_command.assert_called_once_with('AT+SAPBR=0,1')
        self.assertEqual(result, b'OK\r\n')


if __name__ == '__main__':
    unittest.main()
