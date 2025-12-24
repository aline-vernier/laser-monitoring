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
        try:
            tango_host = tango.ApiUtil.get_env_var("TANGO_HOST")
            print(f'Tango host: {tango_host}')
            print(f'Tango version: {tango.__version__}')
        except Exception as e:
            print(f'Exception {e}, no tango host could be found')

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

        self.device_list = [dummy_device]

    def create_devices(self):
        for dev in self.device_list:
            try:
                self.devices[dev['name']] = DeviceMaker.create(dev)
            except Exception as e:
                print(e)


if __name__ == "__main__":

    appli = QApplication(sys.argv)
    appli.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    laser_data = Laser_Data(polling_period=1)
    laser_data.load_config()
    laser_data.create_devices()
    for dev_key in laser_data.devices:
        print(laser_data.devices[dev_key])
    laser_data.show()
    appli.exec_()


