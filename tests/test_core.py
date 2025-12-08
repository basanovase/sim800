import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock the MicroPython modules before importing SIM800
sys.modules['machine'] = MagicMock()
sys.modules['utime'] = MagicMock()

from sim800.core import SIM800


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
        """Test handling of error response"""
        self.sim.send_command = MagicMock(return_value=b'ERROR\r\n')

        result = self.sim.get_network_time()

        self.assertIsNone(result)

    def test_get_network_time_malformed_response(self):
        """Test handling of malformed response"""
        self.sim.send_command = MagicMock(return_value=b'+CCLK: "invalid"\r\nOK\r\n')

        result = self.sim.get_network_time()

        self.assertIsNone(result)

    def test_get_network_time_string_response(self):
        """Test handling when response is already a string"""
        self.sim.send_command = MagicMock(return_value='+CCLK: "24/12/08,14:30:45+04"\r\nOK\r\n')

        result = self.sim.get_network_time()

        self.assertEqual(result['year'], 2024)
        self.assertEqual(result['hour'], 14)


if __name__ == '__main__':
    unittest.main()
