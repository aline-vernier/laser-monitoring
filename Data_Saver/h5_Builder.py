import h5py
import numpy as np
from typing import Any
from threading import Lock
import time
from Data_Saver.Nested_Dir import create_date_folders


class H5Builder:
    def __init__(self):

        self.lock = Lock()  # Thread safety for async operations
        self.defined_datasets = ['rolling_1d', 'static_1d', 'density_2d']

    def create_file(self, file_name: str, root_path: str, devices: dict[str, Any]):
        created_path = create_date_folders(root_path)
        print(f'Created path: {created_path}')
        self.file = created_path / file_name

        """Initialize datasets for each device"""
        with h5py.File(self.file, 'a') as f:
            for device_id, device in devices.items():
                print(f'device id: {device_id}, device graph type: {device.graph_type}')
                print(f'dim_y: {device.shape[0]})')
                dim_y = device.shape[0]
                try:
                    dim_x = device.shape[1]
                except:
                    dim_x = 0
                print(f', dim_x: {dim_x}')

                if device.graph_type in self.defined_datasets:
                    dataset_name = f'devices/{device_id}'

                    if device.graph_type == 'density_2d':
                        _format = {
                            "name": dataset_name,
                            "shape": (0, dim_y, dim_x),  # Start with 0 images
                            "maxshape": (None, dim_y, dim_x),  # Allow unlimited images
                            "dtype": 'i2',
                            "chunks": (1, dim_y, dim_x),  # One image per chunk
                            "compression": 'gzip',
                            "compression_opts": 4
                        }
                    else :
                        _format = {
                            "name": dataset_name,
                            "shape": (dim_x, dim_y),
                            "maxshape": (None, dim_y),
                            "dtype": 'f4',
                            "chunks": (1000, dim_y),
                            "compression": 'gzip',
                            "compression_opts": 4
                        }


                    if dataset_name not in f:
                        # Create dataset using _format dictionary
                        f.create_dataset(
                            name=_format["name"],
                            shape=_format["shape"],  # ← Use _format
                            maxshape=_format["maxshape"],
                            dtype=_format["dtype"],  # ← Use _format
                            chunks=_format["chunks"],  # ← Use _format
                            compression=_format["compression"],
                            compression_opts=_format["compression_opts"]
                        )

                        # Store metadata as attributes
                        f[dataset_name].attrs['device_name'] = device.name
                        f[dataset_name].attrs['graph_type'] = device.graph_type

            print(f"Success! Created datasets for {len(devices)} devices")
    def append_data(self, device_id: str, timestamp: float, value: float):
        """Append a single (timestamp, value) pair to a device's dataset"""

        with self.lock:  # Thread-safe for async operations
            with h5py.File(self.file, 'a') as f:
                dataset_name = f'devices/{device_id}'

                if dataset_name not in f:
                    raise ValueError(f"Dataset {dataset_name} not found")

                dataset = f[dataset_name]
                graph_type = dataset.attrs.get('graph_type')
                print(f'Graph type: {graph_type}')
                if graph_type == 'density_2d':
                    # Resize dataset and add new image
                    dataset.resize((dataset.shape[0] + 1, *dataset.shape[1:]))
                    dataset[-1] = data  # Add image to the last position
                else :
                    current_size = dataset.shape[0]
                
                # Resize and append
                    dataset.resize(current_size + 1, axis=0)
                    dataset[current_size] = [timestamp, value]

    def append_batch(self, device_id: str, data: np.ndarray):
        """Append multiple (timestamp, value) pairs at once

        """
        t_0 = time.time()

        with self.lock:
            with h5py.File(self.file, 'a') as f:
                dataset_name = f'devices/{device_id}'
                print(f'Dataset name: {dataset_name}')
                
                if dataset_name not in f:
                    raise ValueError(f"Dataset {dataset_name} not found")
                
                dataset = f[dataset_name]
                graph_type = dataset.attrs.get('graph_type')

                current_size = dataset.shape[0]
                if graph_type == 'density_2d':
                    # Resize dataset and add new image
                    dataset.resize((dataset.shape[0] + 1, *dataset.shape[1:]))
                    # Add image to the last position
                    dataset[-1] = data
                else:
                    # Resize and append
                    dataset.resize(current_size + 1, axis=0)
                    dataset[current_size:] = data
        print(f'saving batch took {time.time()-t_0}s')
    
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

