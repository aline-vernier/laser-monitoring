import json

def readConfig(configFile: str) -> dict:
    """Read configuration from a JSON file."""
    try:
        with open(configFile, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Configuration file {configFile} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the configuration file {configFile}.")
        return {}
    except Exception as e:
        print(f"An error occurred while reading the configuration file {configFile}: {e}")
        return {}
    
def writeConfig(configFile: str, config: dict) -> None:
    """Write configuration to a JSON file."""
    try:
        with open(configFile, 'w') as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        print(f"An error occurred while writing to the configuration file {configFile}: {e}")
   
if __name__ == "__main__":
    sample_config = {
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
    config_file_path = "./Config/dummy_config.json"
    
    # Write sample configuration to file
    writeConfig(config_file_path, sample_config)
    
    # Read configuration back from file
    loaded_config = readConfig(config_file_path)
    conf = [loaded_config[key] for key in loaded_config]
    print(conf)

