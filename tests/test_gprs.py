import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock the MicroPython modules before importing
sys.modules['machine'] = MagicMock()
sys.modules['utime'] = MagicMock()

from sim800.gprs import SIM800GPRS
from sim800.exceptions import SIM800ConnectionError, SIM800CommandError


class TestAttachGPRS(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800GPRS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800GPRS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim.send_command_with_retry = MagicMock()

    def test_attach_gprs_with_retry(self):
        """Test attaching to GPRS with retry enabled"""
        self.sim.send_command_with_retry.return_value = b'OK\r\n'

        result = self.sim.attach_gprs(retry=True)

        self.sim.send_command_with_retry.assert_called_once_with('AT+CGATT=1', timeout=10000)
        self.assertEqual(result, b'OK\r\n')

    def test_attach_gprs_without_retry(self):
        """Test attaching to GPRS without retry"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.attach_gprs(retry=False)

        self.sim.send_command.assert_called_once_with('AT+CGATT=1', timeout=10000)
        self.assertEqual(result, b'OK\r\n')

    def test_attach_gprs_error(self):
        """Test attach failure raises SIM800ConnectionError"""
        self.sim.send_command_with_retry.side_effect = SIM800CommandError('AT+CGATT=1', 'ERROR')

        with self.assertRaises(SIM800ConnectionError) as ctx:
            self.sim.attach_gprs()

        self.assertIn('GPRS', str(ctx.exception))


class TestDetachGPRS(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800GPRS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800GPRS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()

    def test_detach_gprs_success(self):
        """Test detaching from GPRS"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.detach_gprs()

        self.sim.send_command.assert_called_once_with('AT+CGATT=0')
        self.assertEqual(result, b'OK\r\n')

    def test_detach_gprs_error(self):
        """Test detach failure raises SIM800ConnectionError"""
        self.sim.send_command.side_effect = SIM800CommandError('AT+CGATT=0', 'ERROR')

        with self.assertRaises(SIM800ConnectionError) as ctx:
            self.sim.detach_gprs()

        self.assertIn('GPRS', str(ctx.exception))


class TestSetAPN(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800GPRS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800GPRS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim.send_command_with_retry = MagicMock()

    def test_set_apn_basic(self):
        """Test setting APN with just APN name"""
        self.sim.send_command.return_value = b'OK\r\n'
        self.sim.send_command_with_retry.return_value = b'OK\r\n'

        result = self.sim.set_apn('internet')

        self.sim.send_command.assert_called_once_with('AT+CSTT="internet","",""')
        self.sim.send_command_with_retry.assert_called_once_with('AT+CIICR', timeout=30000)

    def test_set_apn_with_credentials(self):
        """Test setting APN with username and password"""
        self.sim.send_command.return_value = b'OK\r\n'
        self.sim.send_command_with_retry.return_value = b'OK\r\n'

        result = self.sim.set_apn('internet', user='user1', pwd='pass1')

        self.sim.send_command.assert_called_once_with('AT+CSTT="internet","user1","pass1"')

    def test_set_apn_without_retry(self):
        """Test setting APN without retry"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.set_apn('internet', retry=False)

        calls = self.sim.send_command.call_args_list
        self.assertEqual(calls[0][0][0], 'AT+CSTT="internet","",""')
        self.assertEqual(calls[1][0][0], 'AT+CIICR')
        self.assertEqual(calls[1][1]['timeout'], 30000)

    def test_set_apn_empty_raises_error(self):
        """Test empty APN raises ValueError"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.set_apn('')

        self.assertIn('APN', str(ctx.exception))

    def test_set_apn_command_error(self):
        """Test command failure raises SIM800ConnectionError"""
        self.sim.send_command.side_effect = SIM800CommandError('AT+CSTT', 'ERROR')

        with self.assertRaises(SIM800ConnectionError):
            self.sim.set_apn('internet')


class TestGetGSMLocation(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800GPRS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800GPRS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim._decode_response = lambda x: x.decode() if isinstance(x, bytes) else x

    def test_get_gsm_location_success(self):
        """Test successful location retrieval"""
        self.sim.send_command.return_value = b'+CIPGSMLOC: 0,-122.4194,37.7749,2024/12/08,14:30:00\r\nOK\r\n'

        result = self.sim.get_gsm_location()

        self.sim.send_command.assert_called_once_with('AT+CIPGSMLOC=1,1', check_error=False)
        self.assertEqual(result['longitude'], -122.4194)
        self.assertEqual(result['latitude'], 37.7749)
        self.assertEqual(result['date'], '2024/12/08')
        self.assertEqual(result['time'], '14:30:00')

    def test_get_gsm_location_positive_coords(self):
        """Test location with positive coordinates"""
        self.sim.send_command.return_value = b'+CIPGSMLOC: 0,151.2093,-33.8688,2024/12/08,10:00:00\r\nOK\r\n'

        result = self.sim.get_gsm_location()

        self.assertEqual(result['longitude'], 151.2093)
        self.assertEqual(result['latitude'], -33.8688)

    def test_get_gsm_location_error_code(self):
        """Test location error code raises exception"""
        self.sim.send_command.return_value = b'+CIPGSMLOC: 601\r\nOK\r\n'

        with self.assertRaises(SIM800CommandError) as ctx:
            self.sim.get_gsm_location()

        self.assertIn('601', str(ctx.exception))

    def test_get_gsm_location_no_response(self):
        """Test missing CIPGSMLOC response raises exception"""
        self.sim.send_command.return_value = b'ERROR\r\n'

        with self.assertRaises(SIM800CommandError):
            self.sim.get_gsm_location()

    def test_get_gsm_location_malformed_response(self):
        """Test malformed response raises exception"""
        self.sim.send_command.return_value = b'+CIPGSMLOC: 0,invalid\r\n'

        with self.assertRaises(SIM800CommandError) as ctx:
            self.sim.get_gsm_location()

        # Either "incomplete" or "parse" depending on where it fails
        error_msg = str(ctx.exception).lower()
        self.assertTrue('incomplete' in error_msg or 'parse' in error_msg)


class TestGPRSInheritance(unittest.TestCase):
    """Test that GPRS inherits TCP/IP functionality"""

    def setUp(self):
        with patch.object(SIM800GPRS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800GPRS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim.read_response = MagicMock()
            self.sim._decode_response = lambda x: x.decode() if isinstance(x, bytes) else x
            self.sim._validate_port = MagicMock()
            self.sim._validate_ip_or_host = MagicMock()
            self.sim.retries = 3
            self.sim.retry_delay_ms = 500

    def test_has_http_methods(self):
        """Test GPRS class has HTTP methods from TCPIP"""
        self.assertTrue(hasattr(self.sim, 'http_init'))
        self.assertTrue(hasattr(self.sim, 'http_get'))
        self.assertTrue(hasattr(self.sim, 'http_post'))
        self.assertTrue(hasattr(self.sim, 'http_terminate'))

    def test_has_ftp_methods(self):
        """Test GPRS class has FTP methods from TCPIP"""
        self.assertTrue(hasattr(self.sim, 'ftp_init'))
        self.assertTrue(hasattr(self.sim, 'ftp_get_file'))
        self.assertTrue(hasattr(self.sim, 'ftp_put_file'))
        self.assertTrue(hasattr(self.sim, 'ftp_close'))

    def test_has_tcp_methods(self):
        """Test GPRS class has TCP methods from TCPIP"""
        self.assertTrue(hasattr(self.sim, 'start_tcp_connection'))
        self.assertTrue(hasattr(self.sim, 'send_data_tcp'))
        self.assertTrue(hasattr(self.sim, 'close_tcp_connection'))


if __name__ == '__main__':
    unittest.main()
