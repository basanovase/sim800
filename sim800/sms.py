from .core import SIM800

class SIM800SMS(SIM800):
    def set_sms_format(self, format="1"):
        """
        Set SMS format (0 for PDU mode, 1 for text mode).
        """
        return self.send_command(f'AT+CMGF={format}')

    def send_sms(self, number, message):
        """
        Send an SMS message.
        """
        self.send_command(f'AT+CMGS="{number}"')
        self.uart.write(message + chr(26))  # End with Ctrl-Z to send
        return self.read_response()

    def read_sms(self, index=1):
        """
        Read an SMS at a given index.
        """
        return self.send_command(f'AT+CMGR={index}')

    def delete_sms(self, index):
        """
        Delete an SMS at a given index.
        """
        return self.send_command(f'AT+CMGD={index}')

    def read_all_sms(self):
        """
        Read all SMS messages stored in the memory.
        """
        return self.send_command('AT+CMGL="ALL"')

    def delete_all_sms(self):
        """
        Delete all SMS messages.
        """
        return self.send_command('AT+CMGDA="DEL ALL"')
