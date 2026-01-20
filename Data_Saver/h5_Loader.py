import h5py
import numpy as np
import pathlib

class H5Loader:

    def __init__(self, file: pathlib.Path):
        self.file = file
        self._device_groups = self._get_device_groups()
        self._device_datasets = self._get_device_datasets()

    @property
    def device_groups(self):
        return self._device_groups

    @property
    def device_datasets(self):
        return self._device_datasets

    def _get_device_groups(self) -> list:
        with h5py.File(self.file, 'r') as f:
            return list(f.keys())

    def _get_device_datasets(self) -> list:
        with h5py.File(self.file, 'r') as f:
            a_group_key = list(f.keys())[0]
            return list(f[a_group_key])

    def get_device_data(self, group_name: str, dataset_name: str) -> np.ndarray:
            """Retrieve all data for a specific device"""
            with h5py.File(self.file, 'r') as f:
                dataset_name = f'{group_name}/{dataset_name}'
                if dataset_name in f:
                    return f[dataset_name][:]
                else:
                    raise ValueError(f"Dataset {dataset_name} not found")


if __name__ == '__main__':
    h5_file = H5Loader('realtime_data.h5')

    for device_group in h5_file.device_groups:
        for dataset_name in h5_file.device_datasets:
            print(f'Dataset name: {dataset_name}, data: '
                  f'{h5_file.get_device_data(device_group, dataset_name)}')



