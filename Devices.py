from abc import abstractmethod
from tango import DeviceProxy
import numpy as np
import random
import Thread
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QThread



class Device(QWidget):
    """
    Base class for all devices
    """

    def __init__(self, definition: dict):

        self.name = definition['name']
        self.address = definition['address']
        self.type = definition['type']
        

    @abstractmethod
    def get_data(self):
        """Each device implements its own data retrieval"""
        pass




class DummyDevice(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        period_ms = 100
        self.worker = Thread.VirtualDevice(self.name, period_ms)
         # Create thread
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        
        # Connect thread started signal to worker start method
        self.thread.started.connect(self.worker.start)

      
    def start_monitoring(self):
        """Start the device thread"""
        self.thread.start()
    
    def stop_monitoring(self):
        """Stop the device thread"""
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()



class Spectrometer(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.setup()
        self.get_data()
    def setup(self):
        try:
            self.device_proxy = DeviceProxy(self.address)
        except Exception:
            self.device_proxy = None
            raise Exception(f"Could not connect to device: {self.name}")

    def get_data(self):

        if self.device_proxy:
            self.wavelengths = self.device_proxy.read_attribute("lambda").value
            self.spectrum = np.asarray(self.device_proxy.read_attribute("intensity").value)
            print(f'Spectrum: {self.spectrum}')


class BeamAnalyzer(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.properties = {}
        self.setup()
        self.get_data()

    def setup(self):
        try:
            self.device_proxy = DeviceProxy(self.address)
        except Exception:
            self.device_proxy = None
            raise Exception(f"Could not connect to device: {self.name}")

    def get_data(self):
        # BeamAnalyzer-specific logic
        if self.device_proxy:
            self.properties['Centroid X'] = self.device_proxy.read_attribute("CentroidX").value
            self.properties['Centroid Y'] = self.device_proxy.read_attribute("CentroidY").value
            self.properties['Max Intensity'] = self.device_proxy.read_attribute("MaxIntensity").value
            self.properties['Peak X'] = self.device_proxy.read_attribute("PeakX").value
            self.properties['Peak Y'] = self.device_proxy.read_attribute("PeakY").value
            self.properties['Variance X'] = self.device_proxy.read_attribute("VarianceX").value
            self.properties['Variance Y'] = self.device_proxy.read_attribute("VarianceY").value

class EnergyMeter(Device):
    def __init__(self, definition: dict):
        super().__init__(definition)
        self.setup()
        self.get_data()

    def setup(self):
        try:
            self.device_proxy = DeviceProxy(self.address)
        except Exception:
            self.device_proxy = None
            raise Exception(f"Could not connect to device: {self.name}")

    def get_data(self):
        # Spectrometer-specific logic
        if self.device_proxy:
            self.energy = self.device_proxy.read_attribute("energy_1").value
            print(f'Energy: {self.energy}')


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