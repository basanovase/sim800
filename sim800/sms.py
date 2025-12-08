from .core import SIM800
from .exceptions import SIM800SMSError, SIM800CommandError


class SIM800SMS(SIM800):

    def set_sms_format(self, format="1"):
        """
        Set SMS format (0 for PDU mode, 1 for text mode).

        :param format: SMS format ('0' for PDU, '1' for text mode).
        :return: The response from the SIM800 module.
        :raises ValueError: If format is invalid.
        :raises SIM800SMSError: If setting format fails.
        """
        if str(format) not in ('0', '1'):
            raise ValueError("Format must be '0' (PDU) or '1' (text mode)")
        try:
            return self.send_command('AT+CMGF={}'.format(format))
        except SIM800CommandError as e:
            raise SIM800SMSError("Failed to set SMS format: {}".format(e))

    def send_sms(self, number, message):
        """
        Send an SMS message.

        :param number: The recipient phone number.
        :param message: The message text to send.
        :return: The response from the SIM800 module.
        :raises ValueError: If number or message is empty.
        :raises SIM800SMSError: If sending SMS fails.
        """
        if not number:
            raise ValueError("Phone number cannot be empty")
        if not message:
            raise ValueError("Message cannot be empty")

        try:
            self.send_command('AT+CMGS="{}"'.format(number), check_error=False)
            if isinstance(message, str):
                message = message.encode('utf-8')
            self.uart.write(message + bytes([26]))  # End with Ctrl-Z to send
            response = self.read_response()

            response_str = self._decode_response(response)
            if 'ERROR' in response_str:
                raise SIM800SMSError("Failed to send SMS to {}".format(number), number=number)
            return response
        except SIM800CommandError as e:
            raise SIM800SMSError("Failed to send SMS: {}".format(e), number=number)

    def read_sms(self, index=1):
        """
        Read an SMS at a given index.

        :param index: The message index (1-based).
        :return: The SMS content.
        :raises ValueError: If index is invalid.
        :raises SIM800SMSError: If reading SMS fails.
        """
        if not isinstance(index, int) or index < 1:
            raise ValueError("Index must be a positive integer")
        try:
            return self.send_command('AT+CMGR={}'.format(index))
        except SIM800CommandError as e:
            raise SIM800SMSError("Failed to read SMS at index {}: {}".format(index, e))

    def delete_sms(self, index):
        """
        Delete an SMS at a given index.

        :param index: The message index to delete.
        :return: The response from the SIM800 module.
        :raises ValueError: If index is invalid.
        :raises SIM800SMSError: If deleting SMS fails.
        """
        if not isinstance(index, int) or index < 1:
            raise ValueError("Index must be a positive integer")
        try:
            return self.send_command('AT+CMGD={}'.format(index))
        except SIM800CommandError as e:
            raise SIM800SMSError("Failed to delete SMS at index {}: {}".format(index, e))

    def read_all_sms(self):
        """
        Read all SMS messages stored in the memory.

        :return: All stored SMS messages.
        :raises SIM800SMSError: If reading SMS fails.
        """
        try:
            return self.send_command('AT+CMGL="ALL"')
        except SIM800CommandError as e:
            raise SIM800SMSError("Failed to read all SMS: {}".format(e))

    def delete_all_sms(self):
        """
        Delete all SMS messages.

        :return: The response from the SIM800 module.
        :raises SIM800SMSError: If deleting SMS fails.
        """
        try:
            return self.send_command('AT+CMGDA="DEL ALL"')
        except SIM800CommandError as e:
            raise SIM800SMSError("Failed to delete all SMS: {}".format(e))
