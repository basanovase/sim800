from .tcpip import SIM800TCPIP
from .exceptions import SIM800ConnectionError, SIM800CommandError


class SIM800GPRS(SIM800TCPIP):
    """
    GPRS-specific functionality for the SIM800 module.

    Inherits all TCP/IP, HTTP, and FTP functionality from SIM800TCPIP,
    and adds GPRS attachment, APN configuration, and GSM location features.
    """

    def attach_gprs(self, retry=True):
        """
        Attach to the GPRS service.

        :param retry: If True, retry on failure (default True).
        :return: The response from the SIM800 module.
        :raises SIM800ConnectionError: If attaching to GPRS fails.
        """
        try:
            if retry:
                return self.send_command_with_retry('AT+CGATT=1', timeout=10000)
            return self.send_command('AT+CGATT=1', timeout=10000)
        except SIM800CommandError as e:
            raise SIM800ConnectionError("Failed to attach to GPRS: {}".format(e))

    def detach_gprs(self):
        """
        Detach from the GPRS service.

        :return: The response from the SIM800 module.
        :raises SIM800ConnectionError: If detaching from GPRS fails.
        """
        try:
            return self.send_command('AT+CGATT=0')
        except SIM800CommandError as e:
            raise SIM800ConnectionError("Failed to detach from GPRS: {}".format(e))

    def set_apn(self, apn, user='', pwd='', retry=True):
        """
        Set the APN, username, and password for the GPRS connection.

        :param apn: Access Point Name.
        :param user: APN username (optional).
        :param pwd: APN password (optional).
        :param retry: If True, retry on failure (default True).
        :return: The response from the SIM800 module.
        :raises ValueError: If APN is empty.
        :raises SIM800ConnectionError: If setting APN fails.
        """
        if not apn:
            raise ValueError("APN cannot be empty")
        try:
            self.send_command('AT+CSTT="{}","{}","{}"'.format(apn, user, pwd))
            # AT+CIICR can take a long time to establish PDP context
            if retry:
                return self.send_command_with_retry('AT+CIICR', timeout=30000)
            return self.send_command('AT+CIICR', timeout=30000)
        except SIM800CommandError as e:
            raise SIM800ConnectionError("Failed to set APN: {}".format(e))

    def get_gsm_location(self):
        """
        Get the GSM location based on the nearest cell tower.

        :return: Dictionary with longitude, latitude, and timestamp, or raw response if parsing fails.
        :raises SIM800CommandError: If command fails.
        """
        response = self.send_command('AT+CIPGSMLOC=1,1', check_error=False)
        response_str = self._decode_response(response)

        # Try to parse the location response
        # Format: +CIPGSMLOC: 0,longitude,latitude,date,time
        if '+CIPGSMLOC:' in response_str:
            try:
                parts = response_str.split('+CIPGSMLOC:')[1].split(',')
                if len(parts) >= 5 and parts[0].strip() == '0':
                    return {
                        'longitude': float(parts[1].strip()),
                        'latitude': float(parts[2].strip()),
                        'date': parts[3].strip(),
                        'time': parts[4].strip().split('\r')[0]
                    }
            except (IndexError, ValueError):
                pass

        return response
