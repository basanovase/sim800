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
        self.uart.write(command + '\r')
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

    def get_network_time(self):
        """
        Get network time and date.
        """
        return self.send_command('AT+CCLK?')

    def attach_gprs(self):
        """
        Attach to GPRS service.
        """
        return self.send_command('AT+CGATT=1')

    def detach_gprs(self):
        """
        Detach from GPRS service.
        """
        return self.send_command('AT+CGATT=0')

    def set_apn(self, apn, user='', pwd=''):
        """
        Set the APN for the GPRS connection.
        """
        self.send_command(f'AT+CSTT="{apn}","{user}","{pwd}"')
        return self.send_command('AT+CIICR')

    def get_ip_address(self):
        """
        Get local IP address.
        """
        return self.send_command('AT+CIFSR')

    def http_init(self):
        """
        Initialize HTTP service.
        """
        return self.send_command('AT+HTTPINIT')

    def http_set_param(self, param, value):
        """
        Set HTTP parameter.
        """
        return self.send_command(f'AT+HTTPPARA="{param}","{value}"')

    def http_get(self, url):
        """
        Perform HTTP GET method.
        """
        self.http_set_param("URL", url)
        self.send_command('AT+HTTPACTION=0')
        return self.send_command('AT+HTTPREAD')

    def http_post(self, url, data):
        """
        Perform an HTTP POST method.
        """
        self.http_set_param("URL", url)
        self.send_command(f'AT+HTTPDATA={len(data)},10000')
        self.uart.write(data)
        self.send_command('AT+HTTPACTION=1')
        return self.send_command('AT+HTTPREAD')

    def ftp_init(self, server, username, password):
        """
        Initialize FTP session.
        """
        self.send_command(f'AT+FTPCID=1')
        self.send_command(f'AT+FTPSERV="{server}"')
        self.send_command(f'AT+FTPUN="{username}"')
        return self.send_command(f'AT+FTPPW="{password}"')

    def ftp_get_file(self, file_name, file_path):
        """
        Download file from FTP server.
        """
        self.send_command(f'AT+FTPGETNAME="{file_name}"')
        self.send_command(f'AT+FTPGETPATH="{file_path}"')
        return self.send_command('AT+FTPGET=1')

    def adjust_speaker_volume(self, level=5):
        """
        Adjust the speaker volume (0 to 100).
        """
        return self.send_command(f'AT+CLVL={level}')

    def email_init(self):
        """
        Initialize the email functionality.
        """
        return self.send_command('AT+EMAILCID=1')

    def email_config_smtp(self, server, port, username, password):
        """
        Configure SMTP server settings.
        """
        self.send_command(f'AT+SMTPSRV="{server}",{port}')
        self.send_command(f'AT+SMTPAUTH=1,"{username}","{password}"')

    def email_set_recipient(self, recipient):
        """
        Set the recipient of the email.
        """
        return self.send_command(f'AT+SMTPRCPT=0,0,"{recipient}"')

    def email_send_subject(self, subject):
        """
        Set the subject of the email.
        """
        return self.send_command(f'AT+SMTPSUB="{subject}"')

    def email_send_body(self, body):
        """
        Write the body of the email.
        """
        return self.send_command(f'AT+SMTPBODY="{body}"')

    def email_send(self):
        """
        Send the email.
        """
        return self.send_command('AT+SMTPSEND')

    def email_read_response(self):
        """
        Read response from the server after sending the email.
        """
        return self.send_command('AT+SMTPREAD')

    def email_terminate(self):
        """
        Terminate the email session.
        """
        return self.send_command('AT+HTTPTERM')

