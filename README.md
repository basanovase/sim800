# SIM800 MicroPython Library

This library provides an interface for the SIM800 module to perform GSM, GPRS, SMS, and TCP/IP communications using MicroPython on microcontrollers. It includes functions to handle voice calls, SMS, HTTP requests, FTP

## Installation

Copy the `sim800` folder to your MicroPython device filesystem. Make sure the MicroPython firmware supports the `machine` module for UART communication.

## Usage

Here's how to use the library to perform various tasks with the SIM800 module:

### Initialize the SIM800 Module

```python
from sim800 import SIM800
sim800 = SIM800(uart_pin=1, baud=115200)
```
### Send an SMS
```python
sim800.send_sms('+1234567890', 'Hello World')
```

### Make a voice call

```python
sim800.dial_number('+1234567890')
# To hang up the call
sim800.hang_up()
```

### Get network time
```python
time = sim800.get_network_time()
print(time)
```

### HTTP GET Request

```python
sim800.http_init()
sim800.http_set_param("URL", "http://example.com")
response = sim800.http_get()
print(response)
sim800.http_terminate()
```


### FTP File download

```python
sim800.ftp_init(server='ftp.example.com', username='user', password='pass')
file_content = sim800.ftp_get_file('path/to/file.txt', '/remote/path')
print(file_content)
```
