from PyQt6.QtCore import pyqtSignal, QObject, QTimer
from datetime import datetime
import random
import numpy as np

class Data_Acquisition(QObject):
    """Base class that runs in a separate thread"""
    # Signal must be a class attribute
    data_received = pyqtSignal(str, dict)  # (device_id, data)
    error_occurred = pyqtSignal(str, str)  # (device_id, error_message)

    def __init__(self, parent=None):
        super().__init__()
        if parent:
            self.device_id = parent.name
            self.data_type = parent.graph_type
            self.running = False
        else:
            self.device_id = "Virtual Device"
            self.data_type = "rolling_1d"
            self.running = False
        self._t0 = None


    def shape(self):
        """Return the shape of the data produced by this device"""
        self.start()
        data = self.data_generator()
        print(f'data: {data}')
        shape = data['shape']
        self.stop()
        return shape
          

    def start(self):
        """Called when moved to thread"""
        self.running = True
        self.period_ms = 100  # Set default period if not set
        self._t0 = datetime.now().timestamp()
        self._generate_data()  # Start the cycle 
    
    def stop(self):
        self.running = False

class VirtualDevice(Data_Acquisition):

    def __init__(self, parent=None):
        super().__init__(parent)
        

    def setup(self):
        pass

        
    def _generate_data(self):
        
        data = self.data_generator()
        self.data_received.emit(self.device_id, data)
        
        # Schedule next call
        QTimer.singleShot(self.period_ms, self._generate_data)

    def data_generator(self):
        data_generators = {
            'rolling_1d': self.point_data,
            'static_1d': self.waveform_data,
            'density_2d': self.image_data,
        }
        generator = data_generators.get(self.data_type)
        if generator:
            return generator()
        else:
            raise ValueError(f"Unknown graph type: {self.data_type}")
        
    def point_data(self):
        return {
            'x': datetime.now().timestamp() - self._t0,
            'y': random.uniform(0, 100),
            'shape':(1)
        }   

    def waveform_data(self):
        return {
            'x': [i for i in range(100)],
            'y': [random.uniform(0, 100) for _ in range(100)],
            'shape': (100,)
        }
    def image_data(self):
        data = np.random.randint(0, 255, (2048, 1088))
        return {
            'image': data,
            'shape': data.shape
        }
    
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    virtual_device = VirtualDevice()
    virtual_device.data_received.connect(lambda device_id, data: print(f"Data from {device_id}: {data}"))
    virtual_device.start()
    print(f"Data shape: {virtual_device.shape()}")
    virtual_device.stop()

    sys.exit(app.exec())