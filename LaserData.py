import tango
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtCore
import sys
import qdarkstyle
from Devices import DeviceMaker
from Build_Interface import Monitoring_Interface



class Laser_Data(Monitoring_Interface):

    def __init__(self, polling_period: float, buffer_size: int=1000):
        super().__init__(buffer_size)
        self.setup()
        self.devices = {}
        self.polling_period = polling_period
        self._buffer_size = 1000

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
                             ('type', 'dummy device')})
        dummy_device_3 = dict({('name', 'Dummy device 3'),
                        ('address', ""),
                        ('type', 'dummy device')})

        self.device_list = [dummy_device, dummy_device_2]

    def create_devices(self):
        for dev in self.device_list:
            try:
                self.devices[dev['name']] = DeviceMaker.create(dev)

                self.devices[dev['name']].worker.data_received.connect(self._on_device_data)
                self.devices[dev['name']].worker.error_occurred.connect(self._on_device_error)
                self.add_graph(dev['name'])
                print(dev['name'])
            except Exception as e:
                print(e)

    def start_all_devices(self):
        """Start monitoring all devices"""
        for device in self.devices.values():
            device.start_monitoring()

    
    def stop_all_devices(self):
        """Stop monitoring all devices"""
        for device in self.devices.values():
            device.stop_monitoring()

    # ========================================================================
    # SIGNAL HANDLERS (Slots)
    # ========================================================================
    
    def _on_device_data(self, device_id: str, data: dict):
        """Handle data received from any device"""
        # This runs in the main thread (Qt automatically handles this)
        display_text = " | ".join([f"{k}: {v:.2f}" if isinstance(v, float) 
                                    else f"{k}: {v}" 
                                    for k, v in data.items()])
        print(display_text)
    
    def _on_device_error(self, device_id: str, error: str):
        """Handle errors from any device"""
        print('error')
    
    def closeEvent(self, event):
        """Clean up when window closes"""
        self.stop_all_devices()
        event.accept()


if __name__ == "__main__":

    appli = QApplication(sys.argv)
    appli.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    laser_data = Laser_Data(polling_period=1)
    laser_data.load_config()
    laser_data.create_devices()
    for dev_key in laser_data.devices:
        print(laser_data.devices[dev_key])
    laser_data.start_all_devices()
    laser_data.show()
    appli.exec_()


