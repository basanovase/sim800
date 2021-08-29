"""
Flynn McLean

https://www.elecrow.com/wiki/images/2/20/SIM800_Series_AT_Command_Manual_V1.09.pdf

Library for interfacing with SIM800 in Micropython


"""

import machine




class gsm:
    
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




