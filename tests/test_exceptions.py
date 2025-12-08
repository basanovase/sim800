import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock the MicroPython modules before importing
sys.modules['machine'] = MagicMock()
sys.modules['utime'] = MagicMock()

from sim800.core import SIM800
from sim800.tcpip import SIM800TCPIP
from sim800.sms import SIM800SMS
from sim800.gprs import SIM800GPRS
from sim800.exceptions import (
    SIM800Error,
    SIM800CommandError,
    SIM800ConnectionError,
    SIM800InitializationError,
    SIM800SMSError,
    SIM800FTPError,
    SIM800HTTPError,
)


class TestExceptionClasses(unittest.TestCase):
    """Test exception class hierarchy and attributes"""

    def test_base_exception(self):
        """Test SIM800Error is base for all exceptions"""
        self.assertTrue(issubclass(SIM800CommandError, SIM800Error))
        self.assertTrue(issubclass(SIM800ConnectionError, SIM800Error))
        self.assertTrue(issubclass(SIM800InitializationError, SIM800Error))
        self.assertTrue(issubclass(SIM800SMSError, SIM800Error))
        self.assertTrue(issubclass(SIM800FTPError, SIM800Error))
        self.assertTrue(issubclass(SIM800HTTPError, SIM800Error))

    def test_command_error_attributes(self):
        """Test SIM800CommandError has correct attributes"""
        err = SIM800CommandError('AT+TEST', 'ERROR')
        self.assertEqual(err.command, 'AT+TEST')
        self.assertEqual(err.response, 'ERROR')
        self.assertIn('AT+TEST', str(err))

    def test_connection_error_attributes(self):
        """Test SIM800ConnectionError has correct attributes"""
        err = SIM800ConnectionError('Connection failed', ip='192.168.1.1', port=8080)
        self.assertEqual(err.ip, '192.168.1.1')
        self.assertEqual(err.port, 8080)

    def test_sms_error_attributes(self):
        """Test SIM800SMSError has correct attributes"""
        err = SIM800SMSError('SMS failed', number='+1234567890')
        self.assertEqual(err.number, '+1234567890')

    def test_ftp_error_attributes(self):
        """Test SIM800FTPError has correct attributes"""
        err = SIM800FTPError('FTP failed', filename='test.txt', path='/remote/')
        self.assertEqual(err.filename, 'test.txt')
        self.assertEqual(err.path, '/remote/')

    def test_http_error_attributes(self):
        """Test SIM800HTTPError has correct attributes"""
        err = SIM800HTTPError('HTTP failed', url='http://example.com', status_code=404)
        self.assertEqual(err.url, 'http://example.com')
        self.assertEqual(err.status_code, 404)


class TestCoreExceptions(unittest.TestCase):
    """Test exception handling in core module"""

    def setUp(self):
        with patch.object(SIM800, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()

    def test_dial_number_empty_raises_value_error(self):
        """Test dial_number raises ValueError for empty number"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.dial_number('')

        self.assertIn('empty', str(ctx.exception).lower())

    def test_dial_number_none_raises_value_error(self):
        """Test dial_number raises ValueError for None number"""
        with self.assertRaises(ValueError):
            self.sim.dial_number(None)


class TestTCPIPExceptions(unittest.TestCase):
    """Test exception handling in TCPIP module"""

    def setUp(self):
        with patch.object(SIM800TCPIP, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800TCPIP(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim._decode_response = lambda x: x.decode() if isinstance(x, bytes) else x
            self.sim.retries = 3
            self.sim.retry_delay_ms = 500

    def test_start_tcp_invalid_mode(self):
        """Test start_tcp_connection raises ValueError for invalid mode"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.start_tcp_connection('INVALID', '192.168.1.1', 80)

        self.assertIn('TCP', str(ctx.exception))
        self.assertIn('UDP', str(ctx.exception))

    def test_start_tcp_empty_ip(self):
        """Test start_tcp_connection raises ValueError for empty IP"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.start_tcp_connection('TCP', '', 80)

        self.assertIn('empty', str(ctx.exception).lower())

    def test_start_tcp_invalid_port(self):
        """Test start_tcp_connection raises ValueError for invalid port"""
        with self.assertRaises(ValueError):
            self.sim.start_tcp_connection('TCP', '192.168.1.1', 99999)

    def test_start_tcp_connection_fail(self):
        """Test start_tcp_connection raises SIM800ConnectionError on CONNECT FAIL"""
        self.sim.send_command.return_value = b'CONNECT FAIL\r\n'

        with self.assertRaises(SIM800ConnectionError) as ctx:
            self.sim.start_tcp_connection('TCP', '192.168.1.1', 80)

        self.assertEqual(ctx.exception.ip, '192.168.1.1')
        self.assertEqual(ctx.exception.port, 80)

    def test_start_udp_invalid_port(self):
        """Test start_udp_connection raises ValueError for invalid port"""
        with self.assertRaises(ValueError):
            self.sim.start_udp_connection('192.168.1.1', -1)

    def test_receive_udp_invalid_max_length(self):
        """Test receive_data_udp raises ValueError for invalid max_length"""
        with self.assertRaises(ValueError):
            self.sim.receive_data_udp(max_length=0)

        with self.assertRaises(ValueError):
            self.sim.receive_data_udp(max_length=-100)

    def test_http_get_empty_url(self):
        """Test http_get raises ValueError for empty URL"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.http_get('')

        self.assertIn('URL', str(ctx.exception))

    def test_http_set_param_empty_param(self):
        """Test http_set_param raises ValueError for empty param"""
        with self.assertRaises(ValueError):
            self.sim.http_set_param('', 'value')

    def test_ftp_init_empty_server(self):
        """Test ftp_init raises ValueError for empty server"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.ftp_init('', 'user', 'pass')

        self.assertIn('server', str(ctx.exception).lower())

    def test_ftp_init_empty_username(self):
        """Test ftp_init raises ValueError for empty username"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.ftp_init('ftp.example.com', '', 'pass')

        self.assertIn('username', str(ctx.exception).lower())

    def test_ftp_init_empty_password(self):
        """Test ftp_init raises ValueError for empty password"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.ftp_init('ftp.example.com', 'user', '')

        self.assertIn('password', str(ctx.exception).lower())

    def test_ftp_get_file_empty_filename(self):
        """Test ftp_get_file raises ValueError for empty filename"""
        with self.assertRaises(ValueError):
            self.sim.ftp_get_file('', '/path/')

    def test_ftp_get_file_empty_path(self):
        """Test ftp_get_file raises ValueError for empty path"""
        with self.assertRaises(ValueError):
            self.sim.ftp_get_file('file.txt', '')

    def test_ftp_put_file_none_data(self):
        """Test ftp_put_file raises ValueError for None data"""
        with self.assertRaises(ValueError):
            self.sim.ftp_put_file('file.txt', '/path/', None)


class TestSMSExceptions(unittest.TestCase):
    """Test exception handling in SMS module"""

    def setUp(self):
        with patch.object(SIM800SMS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800SMS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()

    def test_set_sms_format_invalid(self):
        """Test set_sms_format raises ValueError for invalid format"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.set_sms_format('2')

        self.assertIn('0', str(ctx.exception))
        self.assertIn('1', str(ctx.exception))

    def test_send_sms_empty_number(self):
        """Test send_sms raises ValueError for empty number"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.send_sms('', 'Hello')

        self.assertIn('number', str(ctx.exception).lower())

    def test_send_sms_empty_message(self):
        """Test send_sms raises ValueError for empty message"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.send_sms('+1234567890', '')

        self.assertIn('message', str(ctx.exception).lower())

    def test_read_sms_invalid_index(self):
        """Test read_sms raises ValueError for invalid index"""
        with self.assertRaises(ValueError):
            self.sim.read_sms(0)

        with self.assertRaises(ValueError):
            self.sim.read_sms(-1)

    def test_delete_sms_invalid_index(self):
        """Test delete_sms raises ValueError for invalid index"""
        with self.assertRaises(ValueError):
            self.sim.delete_sms(0)


class TestGPRSExceptions(unittest.TestCase):
    """Test exception handling in GPRS module"""

    def setUp(self):
        with patch.object(SIM800GPRS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800GPRS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim.send_command_with_retry = MagicMock()
            self.sim._decode_response = lambda x: x.decode() if isinstance(x, bytes) else x
            self.sim.retries = 3
            self.sim.retry_delay_ms = 500

    def test_set_apn_empty(self):
        """Test set_apn raises ValueError for empty APN"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.set_apn('')

        self.assertIn('APN', str(ctx.exception))

    def test_start_tcp_invalid_mode(self):
        """Test start_tcp_connection raises ValueError for invalid mode"""
        with self.assertRaises(ValueError):
            self.sim.start_tcp_connection('FTP', '192.168.1.1', 80)

    def test_start_tcp_empty_ip(self):
        """Test start_tcp_connection raises ValueError for empty IP"""
        with self.assertRaises(ValueError):
            self.sim.start_tcp_connection('TCP', '', 80)

    def test_attach_gprs_error(self):
        """Test attach_gprs raises SIM800ConnectionError on failure"""
        self.sim.send_command_with_retry.side_effect = SIM800CommandError('AT+CGATT=1', 'ERROR')

        with self.assertRaises(SIM800ConnectionError) as ctx:
            self.sim.attach_gprs()

        self.assertIn('GPRS', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
