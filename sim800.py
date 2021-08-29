"""
Flynn McLean

https://www.elecrow.com/wiki/images/2/20/SIM800_Series_AT_Command_Manual_V1.09.pdf

Library for interfacing with SIM800 in Micropython


"""



import machine




class gsm:
    
    """

    Main GSM class - initialise UART pin and BAUD
    
    """
    
    def __init__(self, UART_PIN, BAUD=115200):
        self.UART_PIN = UART_PIN
        self.BAUD = BAUD
        self.gsm = machine.UART(self.UART_PIN, self.BAUD)
        
    def signal_check(self):
        signal = self.gsm.write('AT+CSQ\r')
        return signal

    def available_networks(self):
        networks = self.gsm.write('AT+COPS=?\r')
        return networks

    def is_connected(self):
        conn = self.gsm.write('AT+CREG?\r')
        return conn
    
    def read_sms(self, index=1):
        """
        Read SMS from SIM memory at nominated index
        """
        message = self.gsm.write('AT+CMGR={}'.format(str(index)))
        return message
    
    def read_all_sms(self):
        """
        Read ALL SMS from memory
        """
        messages = self.gsm.write('AT+CMGL"all"')
        return messages
    
    def delete_message(self, index)
        self.gsm.write('AT+CMGD={}'.format(index))
        
    def delete_all_messages(self)
        self.gsm.write('AT+CMGD="all"')
    
    def send_sms(self, number, message):
        """
            Send a message - number must be in format + - example +64XXXXXXXXX 
        """
        self.gsm.write('AT+CMGS="{}"')
        self.gsm.write(str(message))
        #end-of-file marker in hex - potentially needs a leading zero
        self.gsm.write("\x1a")
       

