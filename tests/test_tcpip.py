import unittest
from unittest.mock import MagicMock, patch, call
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

    def test_start_udp_connection(self):
        """Test starting a UDP connection"""
        self.sim.send_command.return_value = b'CONNECT OK\r\n'

        result = self.sim.start_udp_connection('192.168.1.100', 8080)

        self.sim.send_command.assert_called_once_with('AT+CIPSTART="UDP","192.168.1.100","8080"')
        self.assertEqual(result, b'CONNECT OK\r\n')

    def test_start_udp_connection_with_domain(self):
        """Test starting a UDP connection with domain name"""
        self.sim.send_command.return_value = b'CONNECT OK\r\n'

        result = self.sim.start_udp_connection('example.com', 53)

        self.sim.send_command.assert_called_once_with('AT+CIPSTART="UDP","example.com","53"')
        self.assertEqual(result, b'CONNECT OK\r\n')

    def test_send_data_udp_string(self):
        """Test sending string data through UDP"""
        self.sim.read_response.return_value = b'SEND OK\r\n'

        result = self.sim.send_data_udp('Hello UDP')

        self.sim.send_command.assert_called_once_with('AT+CIPSEND=9')
        self.sim.uart.write.assert_called_once_with(b'Hello UDP' + bytes([26]))
        self.assertEqual(result, b'SEND OK\r\n')

    def test_send_data_udp_bytes(self):
        """Test sending bytes data through UDP"""
        self.sim.read_response.return_value = b'SEND OK\r\n'
        test_data = b'\x01\x02\x03\x04'

        result = self.sim.send_data_udp(test_data)

        self.sim.send_command.assert_called_once_with('AT+CIPSEND=4')
        self.sim.uart.write.assert_called_once_with(test_data + bytes([26]))
        self.assertEqual(result, b'SEND OK\r\n')

    def test_send_data_udp_empty(self):
        """Test sending empty data through UDP"""
        self.sim.read_response.return_value = b'SEND OK\r\n'

        result = self.sim.send_data_udp('')

        self.sim.send_command.assert_called_once_with('AT+CIPSEND=0')
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

        self.sim.send_command.assert_called_once_with('AT+CIPCLOSE=1')
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

    def test_start_tcp_connection(self):
        """Test starting a TCP connection still works"""
        self.sim.send_command.return_value = b'CONNECT OK\r\n'

        result = self.sim.start_tcp_connection('TCP', '192.168.1.1', 80)

        self.sim.send_command.assert_called_once_with('AT+CIPSTART="TCP","192.168.1.1","80"')

    def test_get_ip_address(self):
        """Test getting IP address"""
        self.sim.send_command.return_value = b'10.0.0.1\r\n'

        result = self.sim.get_ip_address()

        self.sim.send_command.assert_called_once_with('AT+CIFSR')


if __name__ == '__main__':
    unittest.main()
