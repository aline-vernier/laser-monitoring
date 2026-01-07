
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



