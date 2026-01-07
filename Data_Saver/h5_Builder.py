import h5py
import numpy as np
import pathlib 


class H5Builder:
    def __init__(self, file: pathlib.Path):
        self.file = file

    def create_file(self, devices: list):
        # Define column names and types
        self.columns = []
        for device in devices.values():
            if device.graph_type == 'rolling_1d':
                print(f'Graph type: {device.graph_type}')
                device_id = device.name
                self.columns.append((device_id, 'f4'))
            self.dt = np.dtype(self.columns) # data type

        with h5py.File(self.file, 'a') as f:
            # Create a resizable dataset if it doesn't exist
            if 'laser data' not in f:
                f.create_dataset(
                    'laser data',
                    shape=(0,),              # Start with 0 rows
                    maxshape=(None,),        # Unlimited rows
                    dtype=self.dt,
                    chunks=True              # Enable chunking for resizing
                )

            print(f'dt: {self.dt}')
            print(f'columns: {self.columns}')

    def append_data(self, data: np.ndarray):

        with h5py.File(self.file, 'a') as f:

            dataset = f['laser data']

            # Resize and append
            current_size = dataset.shape[0]
            dataset.resize(current_size + len(data), axis=0)
            dataset[current_size:] = data


if __name__ == "__main__":

    from Device_Classes.Devices import DeviceMaker
    from Config.Config_RW import readConfig
    from random import uniform

    devices = {}
    numPoints = 100
    data = np.array([range(0, numPoints)]).T

    h5_file = H5Builder('./Data_Saver/realtime_data.h5')
    config_file_path = "./Config/dummy_config.json"
    
    # Read configuration back from file
    loaded_config = readConfig(config_file_path)
    device_list = [loaded_config[key] for key in loaded_config]

    for dev in device_list:
        # Dictionary of device objects
        device_id = dev['name']
        device = DeviceMaker.create(dev)
        devices[device_id] = device
        dev_data=[]
        for iter in range(0, numPoints):
            dev_data.append(uniform(8, 12))
        data = np.c_[data, dev_data]
    print(data)


    h5_file.create_file(devices)

    # Read the data back
    with h5py.File('./Data_Saver/realtime_data.h5', 'r') as f:
        data = f['laser data'][:]
        print(f"All data: {data}")
