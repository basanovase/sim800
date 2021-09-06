# sim800
Library for interfacing with SIM800 module in Micropython

Add the sim800 file to the micropython device or the local machine


Use:

import sim800
 
gsm = sim800.gsm(2,115200)
 
signal = gsm.signal_check()

networks = gsm.available_networks()
 

SMS:



read_all_sms()

send_sms('+64XXXXXXXXX',"Blue papers please")
