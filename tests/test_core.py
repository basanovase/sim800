import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock the MicroPython modules before importing SIM800
sys.modules['machine'] = MagicMock()
sys.modules['utime'] = MagicMock()

from sim800.core import SIM800
from sim800.exceptions import SIM800CommandError, SIM800TimeoutError


class TestVoiceCalls(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()

    def test_dial_number(self):
        """Test dialing a phone number"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.dial_number('+1234567890')

        self.sim.send_command.assert_called_once_with('ATD+1234567890;')
        self.assertEqual(result, b'OK\r\n')

    def test_dial_number_with_country_code(self):
        """Test dialing with international format"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.dial_number('+44123456789')

        self.sim.send_command.assert_called_once_with('ATD+44123456789;')

    def test_hang_up(self):
        """Test hanging up a call"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.hang_up()

        self.sim.send_command.assert_called_once_with('ATH')
        self.assertEqual(result, b'OK\r\n')

    def test_hang_up_no_active_call(self):
        """Test hanging up when no call is active"""
        self.sim.send_command.return_value = b'NO CARRIER\r\n'

        result = self.sim.hang_up()

        self.assertEqual(result, b'NO CARRIER\r\n')


class TestGetNetworkTime(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800(1)
            self.sim.uart = MagicMock()

    def test_get_network_time_valid_positive_timezone(self):
        """Test parsing time with positive timezone offset"""
        self.sim.send_command = MagicMock(return_value=b'+CCLK: "24/12/08,14:30:45+04"\r\nOK\r\n')

        result = self.sim.get_network_time()

        self.assertEqual(result['year'], 2024)
        self.assertEqual(result['month'], 12)
        self.assertEqual(result['day'], 8)
        self.assertEqual(result['hour'], 14)
        self.assertEqual(result['minute'], 30)
        self.assertEqual(result['second'], 45)
        self.assertEqual(result['timezone'], '+04')

    def test_get_network_time_valid_negative_timezone(self):
        """Test parsing time with negative timezone offset"""
        self.sim.send_command = MagicMock(return_value=b'+CCLK: "25/06/15,09:15:30-08"\r\nOK\r\n')

        result = self.sim.get_network_time()

        self.assertEqual(result['year'], 2025)
        self.assertEqual(result['month'], 6)
        self.assertEqual(result['day'], 15)
        self.assertEqual(result['hour'], 9)
        self.assertEqual(result['minute'], 15)
        self.assertEqual(result['second'], 30)
        self.assertEqual(result['timezone'], '-08')

    def test_get_network_time_no_timezone(self):
        """Test parsing time without timezone offset"""
        self.sim.send_command = MagicMock(return_value=b'+CCLK: "23/01/01,00:00:00"\r\nOK\r\n')

        result = self.sim.get_network_time()

        self.assertEqual(result['year'], 2023)
        self.assertEqual(result['month'], 1)
        self.assertEqual(result['day'], 1)
        self.assertEqual(result['hour'], 0)
        self.assertEqual(result['minute'], 0)
        self.assertEqual(result['second'], 0)
        self.assertEqual(result['timezone'], '+00')

    def test_get_network_time_error_response(self):
        """Test handling of error response raises exception"""
        self.sim.send_command = MagicMock(return_value=b'ERROR\r\n')

        with self.assertRaises(SIM800CommandError) as ctx:
            self.sim.get_network_time()

        self.assertEqual(ctx.exception.command, 'AT+CCLK?')

    def test_get_network_time_malformed_response(self):
        """Test handling of malformed response raises exception"""
        self.sim.send_command = MagicMock(return_value=b'+CCLK: "invalid"\r\nOK\r\n')

        with self.assertRaises(SIM800CommandError) as ctx:
            self.sim.get_network_time()

        self.assertIn('parse', str(ctx.exception).lower())

    def test_get_network_time_string_response(self):
        """Test handling when response is already a string"""
        self.sim.send_command = MagicMock(return_value='+CCLK: "24/12/08,14:30:45+04"\r\nOK\r\n')

        result = self.sim.get_network_time()

        self.assertEqual(result['year'], 2024)
        self.assertEqual(result['hour'], 14)


class TestSendCommand(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800(1)
            self.sim.uart = MagicMock()
            self.sim.retries = 3
            self.sim.retry_delay_ms = 500

    def test_send_command_timeout_raises_exception(self):
        """Test that empty response raises SIM800TimeoutError when require_response=True"""
        self.sim.uart.any.return_value = False
        self.sim.read_response = MagicMock(return_value=b'')

        with self.assertRaises(SIM800TimeoutError) as ctx:
            self.sim.send_command('AT+TEST', timeout=1000, require_response=True)

        self.assertEqual(ctx.exception.command, 'AT+TEST')
        self.assertEqual(ctx.exception.timeout_ms, 1000)

    def test_send_command_timeout_no_exception_when_not_required(self):
        """Test that empty response returns empty bytes when require_response=False"""
        self.sim.read_response = MagicMock(return_value=b'')

        result = self.sim.send_command('AT+TEST', timeout=1000, require_response=False)

        self.assertEqual(result, b'')

    def test_send_command_error_response(self):
        """Test that ERROR response raises SIM800CommandError"""
        self.sim.read_response = MagicMock(return_value=b'ERROR\r\n')

        with self.assertRaises(SIM800CommandError) as ctx:
            self.sim.send_command('AT+BAD')

        self.assertEqual(ctx.exception.command, 'AT+BAD')

    def test_send_command_success(self):
        """Test successful command returns response"""
        self.sim.read_response = MagicMock(return_value=b'OK\r\n')

        result = self.sim.send_command('AT')

        self.assertEqual(result, b'OK\r\n')


class TestSendCommandWithRetry(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800(1)
            self.sim.uart = MagicMock()
            self.sim.retries = 2
            self.sim.retry_delay_ms = 100
            self.sim._clear_uart_buffer = MagicMock()

    def test_retry_succeeds_on_second_attempt(self):
        """Test command succeeds after first failure"""
        responses = [SIM800TimeoutError('AT', 1000), b'OK\r\n']
        call_count = [0]

        def mock_send_command(*args, **kwargs):
            result = responses[call_count[0]]
            call_count[0] += 1
            if isinstance(result, Exception):
                raise result
            return result

        self.sim.send_command = mock_send_command

        result = self.sim.send_command_with_retry('AT', retries=2)

        self.assertEqual(result, b'OK\r\n')
        self.assertEqual(call_count[0], 2)

    def test_retry_exhausted_raises_last_exception(self):
        """Test that last exception is raised after all retries fail"""
        self.sim.send_command = MagicMock(side_effect=SIM800TimeoutError('AT', 1000))

        with self.assertRaises(SIM800TimeoutError):
            self.sim.send_command_with_retry('AT', retries=2)

        self.assertEqual(self.sim.send_command.call_count, 3)  # 1 + 2 retries


if __name__ == '__main__':
    unittest.main()
