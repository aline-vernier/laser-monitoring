import h5py
import numpy as np
import pathlib
from typing import Dict, Any
from threading import Lock


class H5Builder:
    def __init__(self, file: pathlib.Path):
        self.file = file
        self.lock = Lock()  # Thread safety for async operations
        self.defined_datasets = ['rolling_1d', 'static_1d']

    def create_file(self, devices: dict[str, Any]):
        """Initialize datasets for each device"""
        _format_settings = {"chunks": True, "compression": 'gzip', "compression_opts": 4}
        with h5py.File(self.file, 'a') as f:
            for device_id, device in devices.items():
                group_name = f'{device_id}'

                # Each dataset_spec value is a DatasetSpec object
                for dataset_name, dataset_spec in device.hf5_datasets.items():
                    dataset_address = group_name + f'/{dataset_name}'
                    _format = _format_settings | dataset_spec  # Concatenate the two dictionaries

                    if dataset_address not in f:
                        # Create dataset using _format dictionary
                        f.create_dataset(
                            name=dataset_name,
                            shape=_format["shape"],  # ← Use _format
                            dtype=_format["dtype"],  # ← Use _format
                            chunks=_format["chunks"],  # ← Use _format
                            compression=_format["compression"],
                            compression_opts=_format["compression_opts"]
                        )

                        # Store metadata as attributes
                        f[dataset_address].attrs['device_name'] = device.name
                        f[dataset_address].attrs['graph_type'] = device.graph_type

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
                print(f'Device id: {device_id}, length of data: {len(data)}')
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

class PointDataset:
    def __init__ (self, device: Any):
        pass

        
    


class WaveformDataset:
    pass
class imageDataset:
    pass
class BODataset:
    pass