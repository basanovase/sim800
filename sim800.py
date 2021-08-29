"""
Flynn McLean

https://www.elecrow.com/wiki/images/2/20/SIM800_Series_AT_Command_Manual_V1.09.pdf

Library for interfacing with SIM800 in Micropython


"""



import machine




class gsm:
    
    def __init__(self, UART_PIN, BAUD=115200):
        gsm = machine.UART(UART_PIN, BAUD)
        
    def signal_check(self):
        signal = gsm.write('AT+CSQ\r')
        return signal

    def available_networks(self):
        networks = gsm.write('AT+COPS=?\r')
        return networks

    def is_connected(self):
        conn = gsm.write('AT+CREG?\r')
        return conn


