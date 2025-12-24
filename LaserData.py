import tango
from Devices import DeviceMaker
class Laser_Data:

    def __init__(self):
        self.setup()
        self.devices = {}

    def setup(self):
        try:
            tango_host = tango.ApiUtil.get_env_var("TANGO_HOST")
            print(f'Tango host: {tango_host}')
            print(f'Tango version: {tango.__version__}')
        except Exception as e:
            print(f'Exception {e}, no tango host could be found')

    def load_config(self):  # To load from JSON
        spectrometer = dict({('name', 'Spectrometer 1'),
                             ('address', "SY-SPECTRO_1/Spectrometer/FE1"),
                             ('type', 'spectrometer')})
        beam_analyzer = dict({('name', 'Beam Analyzer 1'),
                             ('address', "FE_CAMERA_1/ImgBeamAnalyzer/1"),
                             ('type', 'beam analyzer')})

        self.device_list = [spectrometer, beam_analyzer]

    def create_devices(self):
        for dev in self.device_list:
            self.devices[dev['name']] = DeviceMaker.create(dev)


if __name__ == "__main__":
    laser_data = Laser_Data()
    laser_data.load_config()
    laser_data.create_devices()
    print(f'Laser data devices: {laser_data.devices}')
    #for dev_key in laser_data.devices:
    #    print(laser_data.devices[dev_key])


