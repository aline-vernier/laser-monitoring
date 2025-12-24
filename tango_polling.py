import tango
import numpy as np

from tango import DeviceProxy
import time

#import serial

###############################################
#               PARAMETERS                    #
###############################################

tango_host = tango.ApiUtil.get_env_var("TANGO_HOST")
print(tango_host)
print(tango.__version__)

polling_period = 60  # In seconds
polling_time = 2*60 # In seconds

nb_loops = int(polling_time / polling_period)

size_of_file = nb_loops * 0.05
print('your file is going to take roughly ' + str(size_of_file) + 'Mb')
print("Do you want to continue ? yes/no : ")
txt = input()

if (txt == 'yes' or txt == 'y' or txt == 'oui'):
    print("ok")

    ###############################################
    #               OPEN PROXIES                  #
    ###############################################

    print("Creating proxy to Tango devices...")
    tango_spectrometer1 = DeviceProxy("SY-SPECTRO_1/Spectrometer/FE1")
    tango_spectrometer2 = DeviceProxy("SY-SPECTRO_1/Spectrometer/FE2")
    tango_spectrometer3 = DeviceProxy("SY-SPECTRO_1/Spectrometer/FE3")
    tango_spectrometer4 = DeviceProxy("SY-SPECTRO_1/Spectrometer/FE4")

    tango_imager = DeviceProxy("FE_camera_1/BaslerCCD/1")
    tango_imager2 = DeviceProxy("FE_camera_3/BaslerCCD/1")
    tango_energymeter = DeviceProxy("FE_EM_1/energymeter/1")
    tango_energymeter2 = DeviceProxy("FE_EM_2/energymeter/1")
    tango_camera = DeviceProxy("FE_CAMERA_1/ImgBeamAnalyzer/1")
    tango_camera2 = DeviceProxy("FE_CAMERA_3/ImgBeamAnalyzer/1")
    tango_temperature1 = DeviceProxy("thermo_1/thermometer/1")
    tango_temperature2 = DeviceProxy("thermo_2/thermometer/1")
    print("Done")

    ###############################################
    #               INITALIZE FILES               #
    ###############################################
    print("starting acquisition loop")
    current_timestamp = time.time()

    wavelength_1 = tango_spectrometer1.read_attribute("lambda").value
    wavelength_1 = np.insert(wavelength_1, 0, current_timestamp)

    wavelength_1_save = np.transpose(wavelength_1[:, None])
    np.savetxt('spectrum1.csv', wavelength_1_save, delimiter=',')

    wavelength_2 = tango_spectrometer2.read_attribute("lambda").value
    wavelength_2 = np.insert(wavelength_2, 0, current_timestamp)

    wavelength_2_save = np.transpose(wavelength_2[:, None])
    np.savetxt('spectrum2.csv', wavelength_2_save, delimiter=',')

    wavelength_3 = tango_spectrometer3.read_attribute("lambda").value
    wavelength_3 = np.insert(wavelength_3, 0, current_timestamp)

    wavelength_3_save = np.transpose(wavelength_3[:, None])
    np.savetxt('spectrum3.csv', wavelength_3_save, delimiter=',')

    wavelength_4 = tango_spectrometer4.read_attribute("lambda").value
    wavelength_4 = np.insert(wavelength_4, 0, current_timestamp)

    wavelength_4_save = np.transpose(wavelength_4[:, None])
    np.savetxt('spectrum4.csv', wavelength_4_save, delimiter=',')

    ###############################################
    #         POLL DATA AND APPEND TO FILE        #
    ###############################################

    for loop in range(0, nb_loops):
        print("looping")
        current_timestamp = time.time()
        spectrum_1 = np.asarray(tango_spectrometer1.read_attribute("intensity").value)
        spectrum_1 = np.insert(spectrum_1, 0, current_timestamp)
        spectrum_1_save = np.transpose(spectrum_1[:, None])

        spectrum_2 = np.asarray(tango_spectrometer2.read_attribute("intensity").value)
        spectrum_2 = np.insert(spectrum_2, 0, current_timestamp)
        spectrum_2_save = np.transpose(spectrum_2[:, None])

        spectrum_3 = np.asarray(tango_spectrometer3.read_attribute("intensity").value)
        spectrum_3 = np.insert(spectrum_3, 0, current_timestamp)
        spectrum_3_save = np.transpose(spectrum_3[:, None])

        spectrum_4 = np.asarray(tango_spectrometer4.read_attribute("intensity").value)
        spectrum_4 = np.insert(spectrum_4, 0, current_timestamp)
        spectrum_4_save = np.transpose(spectrum_4[:, None])

        energy = tango_energymeter.read_attribute("energy_1").value
        energy2 = tango_energymeter2.read_attribute("energy_1").value

        camera_centroidX = tango_camera.read_attribute("CentroidX").value
        camera_centroidY = tango_camera.read_attribute("CentroidY").value
        camera_max_intensity = tango_camera.read_attribute("MaxIntensity").value
        camera_max_PeakX = tango_camera.read_attribute("PeakX").value
        camera_max_PeakY = tango_camera.read_attribute("PeakY").value
        camera_varianceX = tango_camera.read_attribute("VarianceX").value
        camera_varianceY = tango_camera.read_attribute("VarianceY").value

        camera_centroidX2 = tango_camera2.read_attribute("CentroidX").value
        camera_centroidY2 = tango_camera2.read_attribute("CentroidY").value
        camera_max_intensity2 = tango_camera2.read_attribute("MaxIntensity").value
        camera_max_PeakX2 = tango_camera2.read_attribute("PeakX").value
        camera_max_PeakY2 = tango_camera2.read_attribute("PeakY").value
        camera_varianceX2 = tango_camera2.read_attribute("VarianceX").value
        camera_varianceY2 = tango_camera2.read_attribute("VarianceY").value

        temperature1 = tango_temperature1.read_attribute("Temperature").value
        temperature2 = tango_temperature2.read_attribute("Temperature").value

        L = [current_timestamp, temperature1, temperature2, energy,energy2,
             camera_centroidX, camera_centroidY, camera_max_intensity,
             camera_max_PeakX, camera_max_PeakY, camera_varianceX, camera_varianceY,
             camera_centroidX2, camera_centroidY2, camera_max_intensity2,
             camera_max_PeakX2, camera_max_PeakY2, camera_varianceX2, camera_varianceY2]

        with open('spectrum1.csv', 'ab') as f:
            np.savetxt(f, spectrum_1_save, delimiter=',')
        f.close()
        with open('spectrum2.csv', 'ab') as f:
            np.savetxt(f, spectrum_2_save, delimiter=',')
        f.close()
        with open('spectrum3.csv', 'ab') as f:
            np.savetxt(f, spectrum_3_save, delimiter=',')
        f.close()
        with open('spectrum4.csv', 'ab') as f:
            np.savetxt(f, spectrum_4_save, delimiter=',')
        f.close()
        with open("test.txt", 'a') as f:
            f.write(', '.join(map(str, L)) + '\n')
        f.close()

        time.sleep(polling_period)
        print(str(nb_loops - loop) + " loops to go !")

    else:
        print("Operation cancelled by user")
