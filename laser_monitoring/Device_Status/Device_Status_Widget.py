import pathlib
import qdarkstyle
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGridLayout
from PyQt6.QtWidgets import QLabel, QCheckBox
from PyQt6.QtCore import QRect
from laser_monitoring.Device_Classes.Devices import Device, DeviceMaker
from importlib.resources import files



class DeviceChannelWidget(QWidget):
    icon_path = files("laser_monitoring.icons")
    def __init__(self, device: Device):
        super().__init__()
        print(f'icon path = {self.icon_path / 'disconnected.png'}')

        base_style = qdarkstyle.load_stylesheet(qt_api='pyqt6')
        unchecked_icon = str(self.icon_path / "disconnected.png")
        checked_icon = str(self.icon_path / "connected.png")

        custom_style = f"""
        QCheckBox::indicator {{
            width: 50px;
            height: 50px;
        }}
        QCheckBox::indicator:unchecked {{
            image: url("{unchecked_icon}");
        }}
        QCheckBox::indicator:checked {{
            image: url("{checked_icon}");
        }}
        QCheckBox {{
            font: 10pt;
        }}
        """

        self.setStyleSheet(base_style + custom_style)
        self.device_name = QLabel(device.name)
        self.device_type = QLabel(device.type)
        self.setup()

    def setup(self):

        self.hbox = QHBoxLayout()
        self.gridlayout = QGridLayout()
        self.connection_status_checkbox = QCheckBox()
        self.message = QLabel("Not connected yet")
        self.message.setGeometry(QRect(0, 0, 100, 100))  # (x, y, width, height)


        self.gridlayout.addWidget(self.connection_status_checkbox, 0, 0)
        self.gridlayout.addWidget(self.device_name, 0, 1)
        self.gridlayout.addWidget(self.device_type, 0, 2)
        self.gridlayout.addWidget(self.message, 0, 3)

        self.hbox.addLayout(self.gridlayout)
        self.setLayout(self.hbox)




    def update_status(self):
        pass
        
class DeviceChannelsBox(QWidget):
    def __init__(self, devices: list):
        super().__init__()
        self.setup(devices)

    def setup(self, devices: list):
        pass

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    device_def = {
        "name": "Beam profiler",
        "address": "",
        "type": "dummy device 2D",
        "is virtual": True,
        "saving period": 20,
        "polling period": 0.1
    }

    device = DeviceMaker.create(device_def)
    print(device)

    widget = DeviceChannelWidget(device)
    widget.show()

    sys.exit(app.exec())








