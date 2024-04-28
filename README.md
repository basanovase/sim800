# SIM800 MicroPython Library

This library provides an interface for the SIM800 module to perform GSM, GPRS, SMS, and TCP/IP communications using MicroPython on microcontrollers. It includes functions to handle voice calls, SMS, HTTP requests, FTP, and more.

## Installation

Copy the `sim800` folder to your MicroPython device filesystem. Ensure that the MicroPython firmware supports the `machine` module for UART communication.

## Usage

### Initialize the SIM800 Module

```python
from sim800 import SIM800
sim800 = SIM800(uart_pin=1, baud=115200)
```

### Send an SMS


```python

from sim800 import SIM800SMS
sim800 = SIM800SMS(uart_pin=1)
sim800.send_sms('+1234567890', 'Hello World')
```

### Make a Voice Call
```python
from sim800 import SIM800
sim800 = SIM800(uart_pin=1)
sim800.dial_number('+1234567890')

# To hang up the call
sim800.hang_up()
```
### Get Network Time
```python
from sim800 import SIM800
sim800 = SIM800(uart_pin=1)
time = sim800.get_network_time()
print(time)
```
### HTTP GET Request
```python
from sim800 import SIM800TCPIP
sim800 = SIM800TCPIP(uart_pin=1)
sim800.http_init()
sim800.http_set_param("URL", "http://example.com")
response = sim800.http_get()
print(response)
sim800.http_terminate()
```

### FTP Download File
```python
from sim800 import SIM800TCPIP
sim800 = SIM800TCPIP(uart_pin=1)
sim800.ftp_init(server='ftp.example.com', username='user', password='pass')
file_content = sim800.ftp_get_file('path/to/file.txt', '/remote/path')
print(file_content)
```
### Get GSM Location
```python

from sim800 import SIM800GPRS
sim800 = SIM800GPRS(uart_pin=1)
location_info = sim800.get_gsm_location()
print("GSM Location Info:", location_info)
```
