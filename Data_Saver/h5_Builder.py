import h5py
import numpy as np

class h5Builder:
    def __init__(self):
        pass

    def create_file(self, device_list: list):
        # Define column names and types
        self.columns = []
        for device in device_list:
            device_id = device['name']
            self.columns = self.columns.append((device_id, 'f4'))
        dt = np.dtype(self.columns)




# Create or open an HDF5 file
with h5py.File('realtime_data.h5', 'a') as f:
    # Define your column names and data types
    dt = np.dtype([
        ('timestamp', 'f8'),      # float64
        ('temperature', 'f4'),     # float32
        ('pressure', 'f4'),        # float32
        ('sensor_id', 'i4')        # int32
    ])

    # Create a resizable dataset if it doesn't exist
    if 'measurements' not in f:
        dataset = f.create_dataset(
            'measurements',
            shape=(0,),              # Start with 0 rows
            maxshape=(None,),        # Unlimited rows
            dtype=dt,
            chunks=True              # Enable chunking for resizing
        )
    else:
        dataset = f['measurements']

    # Append new data
    new_data = np.array([
        (1234567890.0, 25.5, 1013.25, 1),
        (1234567891.0, 25.6, 1013.20, 1),
    ], dtype=dt)

    # Resize and append
    current_size = dataset.shape[0]
    dataset.resize(current_size + len(new_data), axis=0)
    dataset[current_size:] = new_data

# Read the data back
with h5py.File('realtime_data.h5', 'r') as f:
    data = f['measurements'][:]
    print(f"Temperature column: {data['temperature']}")
    print(f"All data: {data}")
