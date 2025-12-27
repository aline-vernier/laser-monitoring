from abc import abstractmethod
from tango import DeviceProxy
import numpy as np
import random
import Data_Acquisition
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
import time 



class Device(QObject):
    """
    Base class for all devices
    """

    def __init__(self, definition: dict):

        self.name = definition['name']
        self.address = definition['address']
        self.type = definition['type']
        # Create thread
        self.thread = QThread()

    def setup(self):
        try:
            self.device_proxy = DeviceProxy(self.address)
        except Exception:
            self.device_proxy = None
            raise Exception(f"Could not connect to device: {self.name}")
        
    @abstractmethod
    def get_data(self):
        if self.device_proxy:
            for key in self.values:
                self.values[key]=self.device_proxy.read_attribute(key).value
          

    
    def start_device(self):
        """Start the device thread"""
        self.thread.start()

    def stop_device(self):
        """Stop the device thread"""
        self.worker.running = False
        time.sleep(.5)
        self.thread.quit()


class DummyDevice(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        period_ms = 200
        self.labels = {'x_label': 'Time', 
                       'y_label': 'Signal', 'x_units': 's', 'y_units': 'V'}
        self.graph_type = 'rolling_1d'

        # Thread setup
        self.worker = Data_Acquisition.VirtualDevice(self.name, period_ms)
        self.worker.moveToThread(self.thread)
        # Connect thread started signal to worker start method
        self.thread.started.connect(self.worker.start)


class Spectrometer(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.setup()
        self.values=dict({("lambda", []), ("intensity", [])})
    


class BeamAnalyzer(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.properties = {}
        self.setup()
        self.values=dict({("Centroid X", []), ("Centroid X", []), 
                          ('Max Intensity', []), ('Peak X', []), 
                          ('Peak Y', []), ('Variance X',[]),
                          ('Variance Y', [])})


class EnergyMeter(Device):
    def __init__(self, definition: dict, is_virtual):
        super().__init__(definition)
        self.setup()
        self.values=dict({("energy_1", [])})



class DeviceMaker:
    _device_types = {
        'spectrometer': Spectrometer,
        'beam analyzer': BeamAnalyzer,
        'energy meter': EnergyMeter,
        'dummy device' : DummyDevice
    }

    @classmethod
    def create(cls, definition: dict) -> Device:
        device_type = definition.get('type')
        device_class = cls._device_types.get(device_type)
         

        if not device_class:
            raise ValueError(f"Unknown device type: {device_type}")

        return device_class(definition)