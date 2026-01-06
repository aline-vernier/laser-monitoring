import h5py
import numpy as np
import pathlib 

class h5Builder:
    def __init__(self, file: pathlib.Path):
        self.file = file

    def create_file(self, device_list: list):
        # Define column names and types
        self.columns = []
        for device in device_list:
            if device.graph_type == 'rolling_1d':
                device_id = device['name']
                self.columns = self.columns.append((device_id, 'f4'))
                dt = np.dtype(self.columns) # data type

        with h5py.File(self.file, 'a') as f:
            f.create_dataset(
                'laser data',
                shape=(0,),              # Start with 0 rows
                maxshape=(None,),        # Unlimited rows
                dtype=dt,
                chunks=True              # Enable chunking for resizing
            )

    def append_data(self, data: np.ndarray):

        with h5py.File(self.file, 'a') as f:
            dataset = f['laser data']


            # Resize and append
            current_size = dataset.shape[0]
            dataset.resize(current_size + len(data), axis=0)
            dataset[current_size:] = data





if __name__ == "__main__":

    h5_file = h5Builder('realtime_data.h5')
    config_dict = {
    "device_1": {
            "name": "Dummy device 1",
            "address": "",
            "type": "dummy device"
        },
        "device_2": {
            "name": "Dummy device 2",
            "address": "",
            "type": "dummy device 1D"
        },
        "device_3": {
            "name": "Dummy device 3",
            "address": "",
            "type": "dummy device 2D"
        },
        "device_4": {
            "name": "Dummy device 4",
            "address": "",
            "type": "dummy device 2D"
        }
    }
    device_list = [config_dict[key] for key in config_dict]
    h5_file.create_file(device_list)

    # Read the data back
    with h5py.File('realtime_data.h5', 'r') as f:
        data = f['laser data'][:]
        print(f"All data: {data}")