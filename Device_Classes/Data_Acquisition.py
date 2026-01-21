from PyQt6.QtCore import pyqtSignal, QObject, QTimer
from datetime import datetime
import random
import numpy as np
from PIL import Image
import time

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
            self.parent = parent
        else:
            self.device_id = "Virtual Device"
            self.data_type = "static_1d"
            self.running = False
        self._t0 = None

    def start(self):
        """Called when moved to thread"""
        self.running = True
        self.period_ms = 500  # Set default period if not set
        self._t0 = datetime.now().timestamp()
        self._generate_data()  # Start the cycle 
    
    def stop(self):
        self.running = False

class VirtualDevice(Data_Acquisition):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_shapes = {
            'rolling_1d': (1,),
            'static_1d': (100,),
            'density_2d': (808, 608)
        }
        try:
            self.im = np.array(Image.open('./Device_Classes/SampleImages/FOCAL_SPOT.TIFF')).T
        except Exception as e :
            print(f'No image was found, {e}, trying elsewhere')
        try:
            self.im = np.array(Image.open('./SampleImages/FOCAL_SPOT.TIFF')).T
        except Exception as e :
            pass
        self.shape = self._get_datadict_shape()

    def setup(self):
        pass

    def _get_datadict_shape(self) -> dict:
        """Return the shape of the data produced by this device"""
        data = self.data_generator()
        shape = {}

        for key, value in data.items():
            if type(value) is list:
                shape[key] = (len(value),)
            elif type(value) is np.ndarray:
                shape[key] = value.shape
            elif type(value) is float or int:
                shape[key] = (1,)
            else:
                raise Exception(f'Unidentifed type')

        return shape


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
        if self._t0 is None:
            t0 = datetime.now().timestamp()
        else:
            t0 = self._t0

        return {
            'x': datetime.now().timestamp() - t0,
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

    def _generate_data(self):
        data = {}
        for key, attribute in self.parent.attrs.items():
            data[key] = self.parent.device_proxy.read_attribute(attribute).value
        self.data_received.emit(self.device_id, data)

        # Schedule next call
        QTimer.singleShot(self.period_ms, self._generate_data)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    virtual_device = VirtualDevice()
    virtual_device.data_received.connect(lambda device_id, data: print(f"Data from {device_id}: {data}"))
    #virtual_device.start()

    #virtual_device.stop()

    sys.exit(app.exec())