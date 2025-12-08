# SIM800 MicroPython Library

This library provides an interface for the SIM800 module to perform GSM, GPRS, SMS, and TCP/IP communications using MicroPython on microcontrollers. It includes functions to handle voice calls, SMS, HTTP requests, FTP, TCP/UDP sockets, and more.

## Installation

### Using mip (recommended)

```python
import mip
mip.install("github:username/sim800")
```

Or using mpremote from your PC:

```bash
mpremote mip install github:username/sim800
```

### Manual Installation

Copy the `sim800` folder to your MicroPython device filesystem.

## Classes

- `SIM800` - Core module with voice calls, network time, and base AT command handling
- `SIM800SMS` - SMS messaging (send, read, delete)
- `SIM800TCPIP` - TCP/UDP sockets, HTTP, and FTP operations
- `SIM800GPRS` - GPRS attachment, APN configuration, and GSM location (inherits all TCPIP features)
- `SIM800Utils` - Static utility functions for direct UART operations

## Usage

### Initialize the SIM800 Module

```python
from sim800 import SIM800

sim800 = SIM800(uart_pin=1, baud=115200)

# With custom retry configuration
sim800 = SIM800(uart_pin=1, baud=115200, retries=5, retry_delay_ms=1000)
```

### Voice Calls

```python
from sim800 import SIM800

sim800 = SIM800(uart_pin=1)

# Make a call
sim800.dial_number('+1234567890')

# Hang up
sim800.hang_up()
```

### Get Network Time

```python
from sim800 import SIM800

sim800 = SIM800(uart_pin=1)
time = sim800.get_network_time()
print(time)
# {'year': 2024, 'month': 3, 'day': 15, 'hour': 14, 'minute': 30, 'second': 45, 'timezone': '+00'}
```

### Reset Module

```python
from sim800 import SIM800

sim800 = SIM800(uart_pin=1)
sim800.reset()
```

### Send an SMS

```python
from sim800 import SIM800SMS

sim800 = SIM800SMS(uart_pin=1)
sim800.send_sms('+1234567890', 'Hello World')
```

### Read SMS Messages

```python
from sim800 import SIM800SMS

sim800 = SIM800SMS(uart_pin=1)

# Set text mode (required before reading)
sim800.set_sms_format('1')

# Read a specific message by index
message = sim800.read_sms(1)

# Read all messages
all_messages = sim800.read_all_sms()
```

### Delete SMS Messages

```python
from sim800 import SIM800SMS

sim800 = SIM800SMS(uart_pin=1)

# Delete a specific message
sim800.delete_sms(1)

# Delete all messages
sim800.delete_all_sms()
```

### GPRS Connection

```python
from sim800 import SIM800GPRS

sim800 = SIM800GPRS(uart_pin=1)

# Attach to GPRS
sim800.attach_gprs()

# Set APN (required for data connections)
sim800.set_apn('your.apn.here', user='username', pwd='password')

# Get assigned IP address
ip = sim800.get_ip_address()
print(ip)

# Detach when done
sim800.detach_gprs()
```

### TCP Connection

```python
from sim800 import SIM800TCPIP

sim800 = SIM800TCPIP(uart_pin=1)

# Start TCP connection
sim800.start_tcp_connection('TCP', '192.168.1.100', 8080)

# Send data
sim800.send_data_tcp('Hello Server')

# Receive data
response = sim800.receive_data_tcp()

# Close connection
sim800.close_tcp_connection()
```

### UDP Connection

```python
from sim800 import SIM800TCPIP

sim800 = SIM800TCPIP(uart_pin=1)

# Start UDP connection
sim800.start_udp_connection('192.168.1.100', 8080)

# Send data
sim800.send_data_udp('Hello UDP')

# Receive data (with optional max length)
response = sim800.receive_data_udp(max_length=512)

# Close connection
sim800.close_udp_connection()
```

### HTTP GET Request

```python
from sim800 import SIM800TCPIP

sim800 = SIM800TCPIP(uart_pin=1)
sim800.http_init()
response = sim800.http_get('http://example.com/api/data')
print(response)
sim800.http_terminate()
```

### HTTP POST Request

```python
from sim800 import SIM800TCPIP

sim800 = SIM800TCPIP(uart_pin=1)
sim800.http_init()
response = sim800.http_post('http://example.com/api/data', '{"key": "value"}')
print(response)
sim800.http_terminate()
```

### FTP Download File

```python
from sim800 import SIM800TCPIP

sim800 = SIM800TCPIP(uart_pin=1)
sim800.ftp_init(server='ftp.example.com', username='user', password='pass', port=21)
file_content = sim800.ftp_get_file('file.txt', '/remote/path')
print(file_content)
sim800.ftp_close()
```

### FTP Upload File

```python
from sim800 import SIM800TCPIP

sim800 = SIM800TCPIP(uart_pin=1)
sim800.ftp_init(server='ftp.example.com', username='user', password='pass')
sim800.ftp_put_file('upload.txt', '/remote/path', 'File content here')
sim800.ftp_close()
```

### Get GSM Location

```python
from sim800 import SIM800GPRS

sim800 = SIM800GPRS(uart_pin=1)
location = sim800.get_gsm_location()
print(location)
# {'longitude': -122.4194, 'latitude': 37.7749, 'date': '2024/03/15', 'time': '14:30:45'}
```

### Using Utility Functions

```python
from machine import UART
from sim800 import SIM800Utils

uart = UART(1, baudrate=115200)

# Send command and wait for specific response
response = SIM800Utils.send_command(uart, 'AT', wait_for='OK', timeout=2000)

# Wait for a specific response
response = SIM800Utils.wait_for_response(uart, 'CONNECT', timeout=5000)

# Clear UART buffer
SIM800Utils.clear_uart_buffer(uart)
```

## Error Handling

The library provides specific exception types for different error conditions:

```python
from sim800 import (
    SIM800,
    SIM800Error,
    SIM800CommandError,
    SIM800TimeoutError,
    SIM800ConnectionError,
    SIM800InitializationError,
    SIM800SMSError,
    SIM800HTTPError,
    SIM800FTPError,
)

sim800 = SIM800(uart_pin=1)

try:
    sim800.dial_number('+1234567890')
except SIM800TimeoutError as e:
    print('Command timed out:', e.command, 'after', e.timeout_ms, 'ms')
except SIM800CommandError as e:
    print('Command failed:', e.command, 'response:', e.response)
except SIM800Error as e:
    print('SIM800 error:', e)
```

Exception types:
- `SIM800Error` - Base exception for all SIM800 errors
- `SIM800CommandError` - AT command returned an error (includes command and response)
- `SIM800TimeoutError` - Command timed out (includes command and timeout duration)
- `SIM800ConnectionError` - Network connection failed (includes IP and port)
- `SIM800InitializationError` - Module initialization failed
- `SIM800SMSError` - SMS operation failed (includes phone number)
- `SIM800HTTPError` - HTTP operation failed (includes URL and status code)
- `SIM800FTPError` - FTP operation failed (includes filename and path)

## License

MIT License
