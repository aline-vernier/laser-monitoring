class DeviceConnectException(Exception):
    def __init__(self, device_name, message):
        super().__init__(message)
        self.device_name = device_name
        self.message = message

    def __str__(self):
        return f"Could not connect device {self.device_name}: {self.message})"

class DeviceReadException(Exception):
    def __init__(self, device_name, message):
        super().__init__(message)
        self.device_name = device_name
        self.message = message

    def __str__(self):
        return f"Could not read data from device {self.device_name}: {self.message})"

