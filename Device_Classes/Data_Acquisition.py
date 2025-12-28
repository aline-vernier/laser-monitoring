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
        self._t0 = datetime.now().timestamp()
    
    def _generate_data(self):
        if self.running:
            # Simulate device data
            data = {
                'y': random.uniform(1500, 2000)/10,
                'x': datetime.now().timestamp()-self._t0
            }
            self.data_received.emit(self.device_id, data)
        else:
            self.stop()

    
    def stop(self):
        if self.timer:
            self.timer.stop()
        super().stop()

class VirtualDevice_2(Data_Acquisition):
    def start(self):
        """Called when moved to thread"""
        self.running = True
        self.period_ms = 100  # Set default period if not set
        self._t0 = datetime.now().timestamp()
        self._generate_data()  # Start the cycle

    def _generate_data(self):
        if not self.running:
            self.finished.emit()
            return
        
        # Generate and emit data
        data = {
            'y': random.uniform(1500, 2000)/10,
            'x': datetime.now().timestamp() - self._t0
        }
        self.data_received.emit(self.device_id, data)
        
        # Schedule next call
        QTimer.singleShot(self.period_ms, self._generate_data)
    
    def stop(self):
        """Stop will prevent next timer from firing"""
        self.running = False
        # No need to stop a timer - just don't reschedule