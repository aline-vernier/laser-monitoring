from abc import abstractmethod
from tango import DeviceProxy
import Device_Classes.Data_Acquisition as Data_Acquisition
from PyQt6.QtCore import QObject, QThread

from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple, Any

"""
To create new device, just specify it in device list, as Virtual Device 
or Tango Device and add it to the DeviceMaker class
"""

@dataclass
class DeviceConfig:
    name: str
    type: str
    dataset_number: int

    metadata: Optional[Dict] = field(default_factory=dict)
    shape: Optional[Tuple] = None
    input_dim: Optional[int] = None
    output_dim: Optional[int] = None


class Device(QObject):
    """
    Base class for all devices
    """

    def __init__(self, definition: dict):
        super().__init__()
        self.name = definition['name']
        self.address = definition['address']
        self.type = definition['type']
        self.isVirtual = definition['is virtual']
        print(f'Device is virtual: {self.isVirtual is True}')
        self.thread = QThread()


    def _start_thread(self):
        if self.isVirtual:
            self.worker = Data_Acquisition.VirtualDevice(parent=self)
        else:
            self.worker = Data_Acquisition.TangoDevice(parent=self)

        self.worker.moveToThread(self.thread)
        # Connect thread started signal to worker start method
        self.thread.started.connect(self.worker.start)

    def setup(self):
        try:
            self.device_proxy = DeviceProxy(self.address)
        except Exception:
            self.device_proxy = None
            raise Exception(f"Could not connect to device: {self.name}")

    @property
    def shape(self):
        return self.worker.data_shapes[self.graph_type]

    def start_device(self):
        """Start the device thread"""
        self.thread.start()


    def stop_device(self):
        """Stop the device thread"""
        self.worker.running = False
        self.thread.quit()


class DummyDevice(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.labels = {'x_label': 'Time',
                       'y_label': 'Signal', 'x_units': 's', 'y_units': 'V'}
        self.graph_type = 'rolling_1d'

        self._start_thread()


class DummyDevice1D(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.labels = {'x_label': 'Time',
                       'y_label': 'Signal', 'x_units': 's', 'y_units': 'V'}
        self.graph_type = 'static_1d'

        self._start_thread()



class DummyDevice2D(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.labels = {'x_label': 'x',
                       'y_label': 'y', 'x_units': 'px', 'y_units': 'px'}
        self.graph_type = 'density_2d'

        self._start_thread()

class Spectrometer(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.setup()
        self.labels = {'x_label': 'lambda',
                       'y_label': 'Amplitude', 'x_units': 'nm', 'y_units': 'a.u.'}
        self.attrs = {'x': 'lambda', 'y': 'intensity'}
        self.graph_type = 'static_1d'

        self._start_thread()


class BeamAnalyzer(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.properties = {}
        self.setup()
        self.attrs = ('Centroid X', 'Centroid Y', 'Max Intensity',
                      'Peak X', 'Peak Y', 'Variance X', 'Variance Y')
        self.graph_type = None
        self._start_thread()

class EnergyMeter(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.setup()
        self.labels = {'x_label': 'time', 'y_label': 'Energy', 'x-units': '(s)', 'y_units': '(mJ)'}
        self.attrs = {'x': None, 'y': 'energy_1'}
        self.graph_type = 'rolling_1d'
        self._start_thread()


class DeviceMaker:
    _device_types = {
        'spectrometer': Spectrometer,
        'beam analyzer': BeamAnalyzer,
        'energy meter': EnergyMeter,
        'dummy device': DummyDevice,
        'dummy device 1D': DummyDevice1D,
        'dummy device 2D': DummyDevice2D,
    }

    @classmethod
    def create(cls, definition: dict) -> Device:
        device_type = definition.get('type')
        device_class = cls._device_types.get(device_type)

        if not device_class:
            raise ValueError(f"Unknown device type: {device_type}")

        return device_class(definition)


if __name__ == "__main__":
    from PyQt6.QtCore import pyqtSlot
    from PyQt6.QtWidgets import QApplication
    import sys

    #app = QApplication(sys.argv)


    @pyqtSlot(str, dict)
    def on_device_data(data: dict):
        for key, item in data:
            print(f'{key}:{item}')


    # Example usage
    device_def = {
        "name": "Spectrometer",
        "address": "SY-SPECTRO_1/Spectrometer/FE1",
        "type": "spectrometer",
        "is virtual": False
        }

    device = DeviceMaker.create(device_def)
    print(f"Created device: {device.name} of type {device.type}")

    device.start_device()
    device.worker.data_received.connect(on_device_data)


