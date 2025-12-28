import tango
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSlot
from PyQt6 import QtCore
import sys
import qdarkstyle
from Device_Classes.Devices import DeviceMaker
from Build_Interface import Monitoring_Interface
from diagServer.diagServer import diagServer


class Laser_Data(Monitoring_Interface):
    signalLaserDataDict = QtCore.pyqtSignal(object)
    def __init__(self, polling_period: float, buffer_size: int=1000):
        super().__init__(buffer_size)
        self.setup()
        self.devices = {}
        self.polling_period = polling_period
        self._buffer_size = buffer_size
        self.device_data = {}

        self.serv = diagServer(parent=self, data={"state":"starting..."}, name='LaserData') # init the server
        self.serv.start() # start the server thread

    def setup(self):

        tango_host = tango.ApiUtil.get_env_var("TANGO_HOST")
        print(f'Tango host: {tango_host}')
        print(f'Tango version: {tango.__version__}')

    def load_config(self):  # To load from JSON
        spectrometer = dict({('name', 'Spectrometer 1'),
                             ('address', "SY-SPECTRO_1/Spectrometer/FE1"),
                             ('type', 'spectrometer')})
        beam_analyzer = dict({('name', 'Beam Analyzer 1'),
                             ('address', "FE_CAMERA_1/ImgBeamAnalyzer/1"),
                             ('type', 'beam analyzer')})
        energy_meter = dict({('name', 'Energy Meter 1'),
                             ('address', "FE_EM_1/Energymeter/1"),
                             ('type', 'energy meter')})
        dummy_device = dict({('name', 'Dummy device 1'),
                             ('address', ""),
                             ('type', 'dummy device')})
        dummy_device_2 = dict({('name', 'Dummy device 2'),
                             ('address', ""),
                             ('type', 'dummy device 1D')})
        dummy_device_3 = dict({('name', 'Dummy device 3'),
                        ('address', ""),
                        ('type', 'dummy device 2D')})

        self.device_list = [dummy_device, dummy_device_2, dummy_device_3]

    def create_devices(self):
        for dev in self.device_list:
            try:
                # Dictionary of device objects
                device_id = dev['name']
                device = DeviceMaker.create(dev)
                self.devices[device_id] = device

                self.connect_device_signals(device)
                self.add_graph(device)
  
            except Exception as e:
                print(e)

    def connect_device_signals(self, device):
        """Connect device signals to slots"""
        device.worker.data_received.connect(self._on_device_data)
        device.worker.error_occurred.connect(self._on_device_error)

    def start_all_devices(self):
        """Start monitoring all devices"""
        for device in self.devices.values():
            device.start_device()
    
    def stop_all_devices(self):
        """Stop monitoring all devices"""
        for device in self.devices.values():
            device.stop_device()

    # ========================================================================
    # SIGNAL HANDLERS (Slots)
    # ========================================================================
    @pyqtSlot(str, dict)
    def _on_device_data(self, device_id: str, data: dict):
        """Handle data received from any device"""
        device = self.devices.get(device_id)
        self.update_graph(device, data)
        self.signalLaserDataDict.emit(dict(device_id=device_id, data=data)) # Signal for DiagServ
        
    @pyqtSlot(str, str)
    def _on_device_error(self, device_id: str, error: str):
        """Handle errors from any device"""
        print('error')

    @pyqtSlot()
    def closeEvent(self, event):
        """Clean up when window closes"""
        self.stop_all_devices()
        self.serv.stop()
        event.accept()


if __name__ == "__main__":

    appli = QApplication(sys.argv)
    appli.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    laser_data = Laser_Data(polling_period=1)
    laser_data.load_config()
    laser_data.create_devices()
    laser_data.start_all_devices()
    laser_data.show()
    appli.exec_()


