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
