import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock the MicroPython modules before importing
sys.modules['utime'] = MagicMock()

from sim800.utils import SIM800Utils


class TestClearUartBuffer(unittest.TestCase):
    def setUp(self):
        self.uart = MagicMock()

    def test_clear_uart_buffer_with_data(self):
        """Test clearing buffer with pending data"""
        self.uart.any.side_effect = [True, True, False]
        self.uart.read.return_value = b'data'

        SIM800Utils.clear_uart_buffer(self.uart)

        self.assertEqual(self.uart.read.call_count, 2)

    def test_clear_uart_buffer_empty(self):
        """Test clearing empty buffer"""
        self.uart.any.return_value = False

        SIM800Utils.clear_uart_buffer(self.uart)

        self.uart.read.assert_not_called()

    def test_clear_uart_buffer_single_read(self):
        """Test clearing buffer with single chunk"""
        self.uart.any.side_effect = [True, False]
        self.uart.read.return_value = b'single chunk'

        SIM800Utils.clear_uart_buffer(self.uart)

        self.uart.read.assert_called_once()


class TestUtilsStaticMethods(unittest.TestCase):
    """Test that all methods are static and callable without instance"""

    def test_wait_for_response_is_static(self):
        """Test wait_for_response is static method"""
        self.assertTrue(isinstance(
            SIM800Utils.__dict__['wait_for_response'],
            staticmethod
        ))

    def test_clear_uart_buffer_is_static(self):
        """Test clear_uart_buffer is static method"""
        self.assertTrue(isinstance(
            SIM800Utils.__dict__['clear_uart_buffer'],
            staticmethod
        ))

    def test_send_command_is_static(self):
        """Test send_command is static method"""
        self.assertTrue(isinstance(
            SIM800Utils.__dict__['send_command'],
            staticmethod
        ))


class TestWaitForResponseIntegration(unittest.TestCase):
    """Integration-style tests using patch to mock utime at the module level"""

    def test_wait_for_response_returns_decoded_string(self):
        """Test that wait_for_response returns decoded string when response found"""
        uart = MagicMock()
        uart.any.return_value = True
        uart.read.return_value = b'OK\r\n'

        with patch('sim800.utils.utime') as mock_utime:
            mock_utime.ticks_ms.return_value = 0
            mock_utime.ticks_diff.return_value = 0

            result = SIM800Utils.wait_for_response(uart, 'OK', timeout=1000)

        self.assertEqual(result, 'OK\r\n')

    def test_wait_for_response_returns_none_on_timeout(self):
        """Test that wait_for_response returns None on timeout"""
        uart = MagicMock()
        uart.any.return_value = False

        with patch('sim800.utils.utime') as mock_utime:
            mock_utime.ticks_ms.return_value = 0
            # Simulate time passing beyond timeout
            mock_utime.ticks_diff.side_effect = [0, 500, 1001]

            result = SIM800Utils.wait_for_response(uart, 'OK', timeout=1000)

        self.assertIsNone(result)


class TestSendCommandIntegration(unittest.TestCase):
    """Integration-style tests for send_command"""

    def test_send_command_writes_to_uart(self):
        """Test that send_command writes command with carriage return"""
        uart = MagicMock()
        # Use a function to handle any() calls: first False for clear_buffer, then True for response
        any_calls = [0]
        def any_side_effect():
            any_calls[0] += 1
            if any_calls[0] == 1:
                return False  # clear_uart_buffer check
            return True  # wait_for_response checks
        uart.any.side_effect = any_side_effect
        uart.read.return_value = b'OK\r\n'

        with patch('sim800.utils.utime') as mock_utime:
            mock_utime.ticks_ms.return_value = 0
            mock_utime.ticks_diff.return_value = 0
            mock_utime.sleep_ms = MagicMock()

            SIM800Utils.send_command(uart, 'AT')

        uart.write.assert_called_once_with('AT\r')

    def test_send_command_returns_none_on_timeout(self):
        """Test that send_command returns None when no response"""
        uart = MagicMock()
        uart.any.return_value = False

        with patch('sim800.utils.utime') as mock_utime:
            mock_utime.ticks_ms.return_value = 0
            mock_utime.ticks_diff.side_effect = [0, 1000, 2001]

            result = SIM800Utils.send_command(uart, 'AT', timeout=2000)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
