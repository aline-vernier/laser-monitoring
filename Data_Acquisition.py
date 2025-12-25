from PyQt6.QtCore import pyqtSignal, QThread, QTimer
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from datetime import datetime

import random



class Data_Acquisition(QObject):
    """Base class that runs in a separate thread"""
    # Signal must be a class attribute
    data_received = pyqtSignal(str, dict)  # (device_id, data)
    error_occurred = pyqtSignal(str, str)  # (device_id, error_message)
    
    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id
        self.running = False
    
    def stop(self):
        self.running = False


class VirtualDevice(Data_Acquisition):
    """Virtual device that emits data periodically"""
    
    def __init__(self, device_id: str, period_ms: int = 1000):
        super().__init__(device_id)
        self.period_ms = period_ms
        self.timer = None
    
    def start(self):
        """Called when moved to thread"""
        self.running = True
        self.timer = QTimer()
        self.timer.timeout.connect(self._generate_data)
        self.timer.start(self.period_ms)
    
    def _generate_data(self):
        if self.running:
            # Simulate device data
            data = {
                'energy': random.uniform(1500, 2000)/10,
                'timestamp': datetime.now().timestamp()
            }
            self.data_received.emit(self.device_id, data)
        else:
            self.stop()

    
    def stop(self):
        if self.timer:
            self.timer.stop()
        super().stop()

