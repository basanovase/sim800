"""
Flynn McLean

https://www.elecrow.com/wiki/images/2/20/SIM800_Series_AT_Command_Manual_V1.09.pdf

Library for interfacing with SIM800 in Micropython


"""
import machine





class SIM800:
    """
    Class to interface with the SIM800 module. Initialize with UART pin and baud rate.
    """
    def __init__(self, uart_pin, baud=115200):
        self.uart = machine.UART(uart_pin, baud)
    
    def send_command(self, command, timeout=1000):
        """
        Send an AT command and return the response.
        """
        self.uart.write(command + '\r\n')
        return self.uart.readall()

    def signal_quality(self):
        """
        Check signal quality.
        """
        return self.send_command('AT+CSQ')

    def available_networks(self):
        """
        List available networks.
        """
        return self.send_command('AT+COPS=?')

    def network_registration(self):
        """
        Check network registration status.
        """
        return self.send_command('AT+CREG?')

    def read_sms(self, index=1):
        """
        Read an SMS at a given index.
        """
        return self.send_command(f'AT+CMGR={index}')

    def read_all_sms(self):
        """
        Read all SMS messages stored in the memory.
        """
        return self.send_command('AT+CMGL="ALL"')

    def delete_sms(self, index):
        """
        Delete an SMS at a given index.
        """
        self.send_command(f'AT+CMGD={index}')

    def delete_all_sms(self):
        """
        Delete all SMS messages.
        """
        self.send_command('AT+CMGDA="DEL ALL"')

    def send_sms(self, number, message):
        """
        Send an SMS message.
        """
        self.send_command(f'AT+CMGS="{number}"')
        self.uart.write(message + chr(26))

    def dial_number(self, number):
        """
        Dial a phone number.
        """
        return self.send_command(f'ATD{number};')

    def hang_up(self):
        """
        Hang up an ongoing call.
        """
        return self.send_command('ATH')

    def answer_call(self):
        """
        Answer an incoming call.
        """
        return self.send_command('ATA')

    def set_sms_format(self, format="1"):
        """
        Set SMS format (0 for PDU mode, 1 for text mode).
        """
        return self.send_command(f'AT+CMGF={format}')

    def set_text_mode_params(self, fo, vp, pid, dcs):
        """
        Set parameters for text mode SMS.
        """
        return self.send_command(f'AT+CSMP={fo},{vp},{pid},{dcs}')


