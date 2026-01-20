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

class Laser_Data(Monitoring_Interface):
    signalLaserDataDict = QtCore.pyqtSignal(object)
    def __init__(self, polling_period: float, buffer_size: int=1000, verbose: bool=False):
        super().__init__(buffer_size)
        self.setup()
        self.devices = {}
        self.polling_period = polling_period
        self._buffer_size = buffer_size
        self.device_data = {}
        self.verbose = verbose

        self.serv = diagServer(parent=self, data={"state": "starting..."}, name='LaserData') # init the server
        self.serv.start() # start the server thread

        self.data_saver = DataSaver(filename='./Data_Saver/laser_data.h5')
       
    def setup(self):

        tango_host = tango.ApiUtil.get_env_var("TANGO_HOST")
        print(f'Tango host: {tango_host}')
        print(f'Tango version: {tango.__version__}')

    def load_config(self):  # To load from JSON
        config_file_path = "./Config/dummy_config.json"
        
        # Read configuration back from file
        loaded_config = readConfig(config_file_path)
        self.device_list = [loaded_config[key] for key in loaded_config]
 

    def create_devices(self):
        print('Creating devices')
        for dev in self.device_list:
            try:
                # Dictionary of device objects
                device_name = dev['name']
                device = DeviceMaker.create(dev)
                self.devices[device_name] = device
                
                self.connect_device_signals(device)
                self.add_graph(device)
                self.add_stretch()
  
            except Exception as e:
                print(e)

    def configure_h5File(self):
         self.data_saver.start(self.devices)
         

    def connect_device_signals(self, device):
        """Connect device signals to slots"""
        device.worker.data_received.connect(self._on_device_data)
        device.worker.error_occurred.connect(self._on_device_error)
        self.data_saver.buffer_warning.connect(lambda size: print(f"WARNING: Buffer filling up! Size: {size}"))
        self.data_saver.data_saved.connect(lambda count: print(f"Saved batch of {count} points"))

    def start_all_devices(self):
        """Start monitoring all devices"""
        for device in self.devices.values():
            device.start_device()
    
    def stop_all_devices(self):
        """Stop monitoring all devices"""
        for device in self.devices.values():
            device.stop_device()

    #######################################################################
    #                    SIGNAL HANDLERS (Slots)
    #######################################################################

    @pyqtSlot(str, dict)
    def _on_device_data(self, device_name: str, data: dict):
        """Handle data received from any device"""
        device = self.devices.get(device_name)
        self.update_graph(device, data)
        self.signalLaserDataDict.emit(dict(device_name=device_name, data=data)) # Signal for DiagServ

        if self.devices[device_name].graph_type in ['rolling_1d', 'static_1d']:
            if self.devices[device_name].graph_type == 'rolling_1d':
                self.data_saver.on_data_event(device_name, [data['x'], data['y']])

            elif self.devices[device_name].graph_type == 'static_1d':
                print(f'data type: {type(data['y'])}, length: {len(data['y'])}')
                self.data_saver.on_data_event(device_name, data['y'])

        elif self.verbose:
            print(f'Method not implemented for device type: {self.devices[device_name].type}')
        else:
            pass

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
    laser_data = Laser_Data(polling_period=1, verbose=False)
    laser_data.load_config()
    laser_data.create_devices()
    laser_data.configure_h5File()
    laser_data.start_all_devices()
    laser_data.show()
    appli.exec_()


