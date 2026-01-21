from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple, Any
import h5py
from Device_Classes.Devices import DeviceMaker


class H5Builder:
    """
    To create the file structure, takes a list of anything with a name attribute, and a dict as data.

    """
    def __init__(self, file: str):
        self.file = file

    def _create_file_structure(self, devices: list):
        with h5py.File(self.file, 'a') as f:

            for device in devices:
                f.create_group(device.name)
                self._create_dataset_from_config(device, f)

    def _create_dataset_from_config(self, device, f: h5py.File):
        f.create_dataset(
            name=device.name,
            shape=(0, 2),  # Start with 0 rows, 2 columns
            maxshape=(None, 2),  # Unlimited rows
            dtype='f8',  # float64 for both timestamp and value
            chunks=(1000, 2),  # Chunk size for efficient I/O
            compression='gzip',  # Optional: compress data
            compression_opts=4
        )


if __name__ == "__main__":

    data_file = H5Builder('./testfile.h5')

