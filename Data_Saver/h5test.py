import h5py
import numpy as np

# Create a new HDF5 file with a resizable dataset
with h5py.File('example.h5', 'w') as f:
    # Create dataset with initial shape (0, columns) and maxshape allowing unlimited rows
    dataset = f.create_dataset('data',
                               shape=(0, 5),  # Start with 0 rows, 5 columns
                               maxshape=(None, 5),  # Allow unlimited rows
                               dtype='float32',
                               chunks=True)  # Enable chunking for resizing

# Append data
with h5py.File('example.h5', 'a') as f:
    dataset = f['data']

    for i in range(1, 20):
        # Create new data to append
        new_data = np.random.rand(10, 5)  # 10 new rows

        # Resize dataset to accommodate new data
        current_size = dataset.shape[0]
        dataset.resize(current_size + new_data.shape[0], axis=0)

        # Write new data
        dataset[current_size:] = new_data