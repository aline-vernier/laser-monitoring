from PyQt6.QtCore import pyqtSignal, QObject, QTimer
from datetime import datetime
import random
from importlib.resources import files
from PIL import Image
import numpy as np

image_path = files("laser_monitoring.Device_Classes.SampleImages") / "FOCAL_SPOT.TIFF"

class Data_Acquisition(QObject):
    """Base class that runs in a separate thread"""
    # Signal must be a class attribute
    data_received = pyqtSignal(str, dict, float)  # (device_id, data, timestamp)
    error_occurred = pyqtSignal(str, str)  # (device_id, error_message)

    def __init__(self, parent=None):
        super().__init__()
        if parent:
            self.device_id = parent.name
            self.data_type = parent.graph_type
            self.polling_period = parent.polling_period
            self.running = False
            self.parent = parent
        else:
            self.device_id = "Virtual Device"
            self.data_type = "rolling_1d"
            self.running = False
            self.polling_period = 2
        self._t0 = None


          

    def start(self):
        """Called when moved to thread"""
        self.running = True
        self.period_ms = int(self.polling_period*1000)  # Set default period if not set
        self._t0 = datetime.now().timestamp()
        self._generate_data()  # Start the cycle 
    
    def stop(self):
        self.running = False

class VirtualDevice(Data_Acquisition):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_shapes = {
            'rolling_1d': (1,),
            'static_1d': (2048,),
            'density_2d': (808, 608)
        }
        #self.im = np.array(Image.open('./Device_Classes/SampleImages/FOCAL_SPOT.TIFF')).T
        self.im = np.array(Image.open(image_path)).T

    def setup(self):
        pass

    def _generate_data(self):
        data = self.data_generator()
        timestamp = (datetime.now()).timestamp()
        self.data_received.emit(self.device_id, data, timestamp)
        
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
            'y': random.uniform(0, 100)
        }   

    def waveform_data(self):
        data_shape = self.data_shapes['static_1d'][0]
        return {
            'x': [i for i in range(data_shape)],
            'y': [random.uniform(0, 100) for _ in range(data_shape)],
        }

    def image_data(self):
        data_shape = self.data_shapes['density_2d']
        data = self.im + np.random.randint(0, 20, data_shape)
        return {
            'image': data,
        }


class TangoDevice(Data_Acquisition):
    def __init__(self, parent=None):
        super().__init__(parent)

    def setup(self):
        pass

    @property
    def data_shapes(self):
        _data_shape = dict({})
    
        for key, attribute in self.parent.attrs.items():
            if attribute is not None: 
                print (f'Getting value from key : {key}, attribute: {attribute}')
                _data_shape[key]=np.shape(self.parent.device_proxy.read_attribute(attribute).value)
                if _data_shape[key] == ():
                    _data_shape[key] = (1,)
                print (f'Attribute value: {_data_shape[key]}')
        return _data_shape

    def _generate_data(self):
        data = {}
        timestamp = (datetime.now()).timestamp()

        for key, attribute in self.parent.attrs.items():
            if attribute is not None :
                data[key] = self.parent.device_proxy.read_attribute(attribute).value
            else : 
                data[key] = datetime.now().timestamp() - self._t0
        self.data_received.emit(self.device_id, data, timestamp)

        # Schedule next call
        QTimer.singleShot(self.period_ms, self._generate_data)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    virtual_device = VirtualDevice()
    virtual_device.data_received.connect(lambda device_id, data, timestamp:
                                         print(f"Data from {device_id}: {data}, timestamp: {timestamp}"))
    virtual_device.start()
    print(f"From Data Acquisition ; Data shape: {virtual_device.shape()}")
    virtual_device.stop()

    sys.exit(app.exec())