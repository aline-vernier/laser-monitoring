import h5py
import numpy as np
import pathlib 

import h5py
import numpy as np
import pathlib
from typing import Dict, Any
from threading import Lock

class H5Builder:
    def __init__(self, file: pathlib.Path):
        self.file = file
        self.lock = Lock()  # Thread safety for async operations
        
    def create_file(self, devices: Dict[str, Any]):
        """Initialize datasets for each device"""
        with h5py.File(self.file, 'a') as f:
            for device_id, device in devices.items():
                if device.graph_type == 'rolling_1d':
                    dataset_name = f'devices/{device_id}'
                    print(f'Dataset Name {dataset_name}')
                    
                    if dataset_name not in f:
                        # Create dataset with 2 columns: timestamp and value
                        f.create_dataset(
                            dataset_name,
                            shape=(0, 2),           # Start with 0 rows, 2 columns
                            maxshape=(None, 2),     # Unlimited rows
                            dtype='f8',             # float64 for both timestamp and value
                            chunks=(1000, 2),       # Chunk size for efficient I/O
                            compression='gzip',     # Optional: compress data
                            compression_opts=4
                        )
                        
                        # Store metadata as attributes
                        f[dataset_name].attrs['device_name'] = device.name
                        f[dataset_name].attrs['graph_type'] = device.graph_type
                        
        print(f"Created datasets for {len(devices)} devices")
    
    def append_data(self, device_id: str, timestamp: float, value: float):
        """Append a single (timestamp, value) pair to a device's dataset"""
        with self.lock:  # Thread-safe for async operations
            with h5py.File(self.file, 'a') as f:
                dataset_name = f'devices/{device_id}'
                
                if dataset_name not in f:
                    raise ValueError(f"Dataset {dataset_name} not found")
                
                dataset = f[dataset_name]
                current_size = dataset.shape[0]
                
                # Resize and append
                dataset.resize(current_size + 1, axis=0)
                dataset[current_size] = [timestamp, value]

    def append_batch(self, device_id: str, data: np.ndarray):
        """Append multiple (timestamp, value) pairs at once
        
        Args:
            device_id: Device identifier
            data: Nx2 array where column 0 is timestamps, column 1 is values
        """
        with self.lock:
            with h5py.File(self.file, 'a') as f:
                dataset_name = f'devices/{device_id}'
                print(f'Dataset name: {dataset_name}')
                
                if dataset_name not in f:
                    raise ValueError(f"Dataset {dataset_name} not found")
                
                dataset = f[dataset_name]
                current_size = dataset.shape[0]
                
                # Resize and append
                dataset.resize(current_size + len(data), axis=0)
                dataset[current_size:] = data
    
    def get_device_data(self, device_id: str) -> np.ndarray:
        """Retrieve all data for a specific device"""
        with h5py.File(self.file, 'r') as f:
            dataset_name = f'devices/{device_id}'
            print(f'dataset name: {dataset_name}')
            if dataset_name in f:
                return f[dataset_name][:]
            else:
                raise ValueError(f"Dataset {dataset_name} not found")
    
    def get_all_devices(self) -> list:
        """Get list of all device IDs"""
        with h5py.File(self.file, 'r') as f:
            if 'devices' in f:
                return list(f['devices'].keys())
            return []

if __name__ == "__main__":

    from Config.Config_RW import readConfig
    from Device_Classes.Devices import DeviceMaker
    import random
    import time
    # Initialize
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
    builder = H5Builder(pathlib.Path("measurements.h5"))

    builder.create_file(devices)

    t_0 = time.time()
    for device in devices.values():
        if device.graph_type == 'rolling_1d':
            builder.append_data(device.name, timestamp=time.time()-t_0, value = random.uniform(8, 12))

    # Or batch append  
    for device in devices.values():
        if device.graph_type == 'rolling_1d':
            data_batch = np.array([
                [time.time()-t_0, random.uniform(8, 12)], 
                [time.time()-t_0, random.uniform(8, 12)], 
                [time.time()-t_0, random.uniform(8, 12)]
                ])
            builder.append_batch(device.name, data_batch)


    # Read back
    for device in devices.values():
        if device.graph_type == 'rolling_1d':
            print(f'Data: {builder.get_device_data(device.name)}')



