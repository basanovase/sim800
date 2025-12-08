import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock the MicroPython modules before importing
sys.modules['machine'] = MagicMock()
sys.modules['utime'] = MagicMock()

from sim800.sms import SIM800SMS
from sim800.exceptions import SIM800SMSError, SIM800CommandError


class TestSMSFormat(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800SMS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800SMS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()

    def test_set_sms_format_text_mode(self):
        """Test setting SMS format to text mode"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.set_sms_format('1')

        self.sim.send_command.assert_called_once_with('AT+CMGF=1')
        self.assertEqual(result, b'OK\r\n')

    def test_set_sms_format_pdu_mode(self):
        """Test setting SMS format to PDU mode"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.set_sms_format('0')

        self.sim.send_command.assert_called_once_with('AT+CMGF=0')

    def test_set_sms_format_accepts_int(self):
        """Test setting SMS format with integer"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.set_sms_format(1)

        self.sim.send_command.assert_called_once_with('AT+CMGF=1')

    def test_set_sms_format_invalid_raises_error(self):
        """Test invalid format raises ValueError"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.set_sms_format('2')

        self.assertIn('0', str(ctx.exception))
        self.assertIn('1', str(ctx.exception))

    def test_set_sms_format_command_error(self):
        """Test command failure raises SIM800SMSError"""
        self.sim.send_command.side_effect = SIM800CommandError('AT+CMGF=1', 'ERROR')

        with self.assertRaises(SIM800SMSError):
            self.sim.set_sms_format('1')


class TestSendSMS(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800SMS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800SMS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()
            self.sim.read_response = MagicMock()
            self.sim._decode_response = lambda x: x.decode() if isinstance(x, bytes) else x

    def test_send_sms_success(self):
        """Test successful SMS sending"""
        self.sim.send_command.return_value = b'> '
        self.sim.read_response.return_value = b'+CMGS: 1\r\nOK\r\n'

        result = self.sim.send_sms('+1234567890', 'Hello World')

        self.sim.send_command.assert_called_once_with('AT+CMGS="+1234567890"', check_error=False)
        self.sim.uart.write.assert_called_once_with(b'Hello World' + bytes([26]))
        self.assertEqual(result, b'+CMGS: 1\r\nOK\r\n')

    def test_send_sms_bytes_message(self):
        """Test sending SMS with bytes message"""
        self.sim.send_command.return_value = b'> '
        self.sim.read_response.return_value = b'+CMGS: 1\r\nOK\r\n'

        result = self.sim.send_sms('+1234567890', b'Hello Bytes')

        self.sim.uart.write.assert_called_once_with(b'Hello Bytes' + bytes([26]))

    def test_send_sms_empty_number_raises_error(self):
        """Test empty phone number raises ValueError"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.send_sms('', 'Hello')

        self.assertIn('number', str(ctx.exception).lower())

    def test_send_sms_empty_message_raises_error(self):
        """Test empty message raises ValueError"""
        with self.assertRaises(ValueError) as ctx:
            self.sim.send_sms('+1234567890', '')

        self.assertIn('message', str(ctx.exception).lower())

    def test_send_sms_error_response(self):
        """Test ERROR response raises SIM800SMSError"""
        self.sim.send_command.return_value = b'> '
        self.sim.read_response.return_value = b'ERROR\r\n'

        with self.assertRaises(SIM800SMSError) as ctx:
            self.sim.send_sms('+1234567890', 'Hello')

        self.assertEqual(ctx.exception.number, '+1234567890')


class TestReadSMS(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800SMS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800SMS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()

    def test_read_sms_success(self):
        """Test reading SMS at index"""
        self.sim.send_command.return_value = b'+CMGR: "REC READ","+1234567890","","24/12/08,10:30:00+00"\r\nHello\r\nOK\r\n'

        result = self.sim.read_sms(1)

        self.sim.send_command.assert_called_once_with('AT+CMGR=1')

    def test_read_sms_custom_index(self):
        """Test reading SMS at custom index"""
        self.sim.send_command.return_value = b'OK\r\n'

        self.sim.read_sms(5)

        self.sim.send_command.assert_called_once_with('AT+CMGR=5')

    def test_read_sms_invalid_index_zero(self):
        """Test index 0 raises ValueError"""
        with self.assertRaises(ValueError):
            self.sim.read_sms(0)

    def test_read_sms_invalid_index_negative(self):
        """Test negative index raises ValueError"""
        with self.assertRaises(ValueError):
            self.sim.read_sms(-1)

    def test_read_sms_invalid_index_string(self):
        """Test string index raises ValueError"""
        with self.assertRaises(ValueError):
            self.sim.read_sms('1')

    def test_read_sms_command_error(self):
        """Test command failure raises SIM800SMSError"""
        self.sim.send_command.side_effect = SIM800CommandError('AT+CMGR=1', 'ERROR')

        with self.assertRaises(SIM800SMSError):
            self.sim.read_sms(1)


class TestDeleteSMS(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800SMS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800SMS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()

    def test_delete_sms_success(self):
        """Test deleting SMS at index"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.delete_sms(1)

        self.sim.send_command.assert_called_once_with('AT+CMGD=1')
        self.assertEqual(result, b'OK\r\n')

    def test_delete_sms_invalid_index(self):
        """Test invalid index raises ValueError"""
        with self.assertRaises(ValueError):
            self.sim.delete_sms(0)

    def test_delete_sms_command_error(self):
        """Test command failure raises SIM800SMSError"""
        self.sim.send_command.side_effect = SIM800CommandError('AT+CMGD=1', 'ERROR')

        with self.assertRaises(SIM800SMSError):
            self.sim.delete_sms(1)


class TestReadAllSMS(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800SMS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800SMS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()

    def test_read_all_sms_success(self):
        """Test reading all SMS messages"""
        self.sim.send_command.return_value = b'+CMGL: 1,"REC READ"...\r\nOK\r\n'

        result = self.sim.read_all_sms()

        self.sim.send_command.assert_called_once_with('AT+CMGL="ALL"')

    def test_read_all_sms_command_error(self):
        """Test command failure raises SIM800SMSError"""
        self.sim.send_command.side_effect = SIM800CommandError('AT+CMGL="ALL"', 'ERROR')

        with self.assertRaises(SIM800SMSError):
            self.sim.read_all_sms()


class TestDeleteAllSMS(unittest.TestCase):
    def setUp(self):
        with patch.object(SIM800SMS, '__init__', lambda self, *args, **kwargs: None):
            self.sim = SIM800SMS(1)
            self.sim.uart = MagicMock()
            self.sim.send_command = MagicMock()

    def test_delete_all_sms_success(self):
        """Test deleting all SMS messages"""
        self.sim.send_command.return_value = b'OK\r\n'

        result = self.sim.delete_all_sms()

        self.sim.send_command.assert_called_once_with('AT+CMGDA="DEL ALL"')
        self.assertEqual(result, b'OK\r\n')

    def test_delete_all_sms_command_error(self):
        """Test command failure raises SIM800SMSError"""
        self.sim.send_command.side_effect = SIM800CommandError('AT+CMGDA="DEL ALL"', 'ERROR')

        with self.assertRaises(SIM800SMSError):
            self.sim.delete_all_sms()


if __name__ == '__main__':
    unittest.main()
