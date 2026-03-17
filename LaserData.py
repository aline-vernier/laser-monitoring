import tango
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSlot
from PyQt6 import QtCore
import sys
import qdarkstyle
from Device_Classes.Devices import DeviceMaker
from Build_Interface import Monitoring_Interface
from diagServer.diagServer import diagServer
from Config.Config_RW import readConfig
from Data_Saver.Data_Saver import DataSaver
from Data_Saver.Data_Scheduler import DataSaveScheduler
import pathlib

class Laser_Data(Monitoring_Interface):
    signalLaserDataDict = QtCore.pyqtSignal(object)

    def __init__(self, polling_period: float, buffer_size: int = 1000, config_file: str = "./Config/tangoVM_config.json",
                 verbose: bool = False, filename: str = 'laser_data.h5', root_path: str = './Data',
                 data_flush_period: int = 30):
        super().__init__()
        self.verbose = verbose
        self.config_file = config_file

        self.setup(filename, root_path, data_flush_period)
        self.devices = {}
        self.polling_period = polling_period
        self._buffer_size = buffer_size

        self.data_saver = DataSaver(flush_interval=self.data_flush_period)
        self.serv = diagServer(parent=self, data={"state": "starting..."}, name='LaserData') # init the server
        self.serv.start()  # start the server thread


    def setup(self, filename, root_path, data_flush_period):

        tango_host = tango.ApiUtil.get_env_var("TANGO_HOST")
        print(f'Tango host: {tango_host}')
        print(f'Tango version: {tango.__version__}')
        self.root_path = root_path
        self.filename = filename
        self.data_flush_period = data_flush_period

        self.connect_button_signals()

    def load_config(self):  # To load from JSON

        # Read configuration back from file
        loaded_config = readConfig(self.config_file)
        self.device_list = [loaded_config[key] for key in loaded_config]
 

    def create_devices(self):
        print('Creating devices')
        for dev in self.device_list:
            try:
                # Dictionary of device objects
                device_name = dev['name']
                device = DeviceMaker.create(dev, polling_period=dev['polling period'],
                                            saving_period=dev['saving period'])

                self.devices[device_name] = device
                self.connect_device_signals(device)
                self.add_graph(device)
                self.add_stretch()
  
            except Exception as e:
                print(e)

    def configure_h5File(self):
        self.data_saver.start(self.devices, filename=self.filename, root_path=self.root_path)

    def connect_device_signals(self, device):
        """Connect device signals to slots"""
        device.worker.data_received.connect(self._on_device_data)
        device.worker.error_occurred.connect(self._on_device_error)
        self.data_saver.buffer_warning.connect(lambda size: print(f"WARNING: Buffer filling up! Size: {size}"))
        self.data_saver.data_saved.connect(lambda count: print(f"Saved batch of {count} points"))

    def connect_button_signals(self):
        self.start_request.connect(self._on_start_request)
        self.stop_request.connect(self._on_stop_request)
        self.update_from_interface.connect(self._on_update_interface)


    def start_all_devices(self):
        """Start monitoring all devices"""

        for device_name, device in self.devices.items():
            self.scheduler.register_device(device_name, saving_period=device.saving_period)
            device.start_device()
            print(f'Starting devices')

    def stop_all_devices(self):
        """Stop monitoring all devices"""
        for device in self.devices.values():
            device.stop_device()

    #######################################################################
    #                    SIGNAL HANDLERS (Slots)
    #######################################################################

    @pyqtSlot(str, dict, float)
    def _on_device_data(self, device_name: str, data: dict, timestamp: float):
        """Handle data received from any device"""
        device = self.devices.get(device_name)
        self.update_graph(device, data)
        self.signalLaserDataDict.emit(dict(device_name=device_name, data=data)) # Signal for DiagServ

        if self.devices[device_name].graph_type in ['rolling_1d', 'static_1d', 'density_2d']:
            if self.devices[device_name].graph_type in ('rolling_1d', 'static_1d'):
                _data = data['y']

            elif self.devices[device_name].graph_type == 'density_2d':
                _data = data['image']

            else:
                raise Exception('Graph type not handled')

            self.scheduler.on_data_received(device_name, _data, timestamp)


        elif self.verbose:
            print(f'Method not implemented for device type: {self.devices[device_name].type}')
        else:
            pass

    @pyqtSlot()
    def _on_start_request(self):
        try:

            self.scheduler = DataSaveScheduler(self.data_saver.on_data_event)
            self.start_all_devices()
            self.configure_h5File()
            self.update_to_running()
        except Exception as e:
            print(f'Exception {e} starting devices')

    def _on_stop_request(self):
        try:
            self.stop_all_devices()
            self.update_to_stopped()
            self.data_saver.stop()
        except Exception as e:
            print(f'Exception {e} stopping devices')

    def _on_update_interface(self):
        self.root_path = pathlib.Path(self.root_path_input.text())
        self.filename = self.file_name_input.text()
        print(f'New root path: {pathlib.Path(self.root_path_input.text())}')
        print(f'New file name: {self.file_name_input.text()}')

    @pyqtSlot(str, str)
    def _on_device_error(self, device_id: str, error: str):
        """Handle errors from any device"""
        print('error')

    @pyqtSlot()
    def closeEvent(self, event):
        """Clean up when window closes"""
        self.stop_all_devices()
        self.serv.stop()
        self.data_saver.stop()
        event.accept()


if __name__ == "__main__":

    appli = QApplication(sys.argv)
    appli.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    laser_data = Laser_Data(polling_period=1, verbose=False, filename='new_laser_data.h5',
                            root_path='C:/Users/APPLI/Python/Older versions/laser-monitoring/Data',
                            config_file="./Config/dummy_config.json",
                            data_flush_period=5)
    laser_data.load_config()
    laser_data.create_devices()
    laser_data.show()
    appli.exec_()


