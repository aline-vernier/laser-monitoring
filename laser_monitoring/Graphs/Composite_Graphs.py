from laser_monitoring.Graphs.Graph_Maker import GraphMaker
from laser_monitoring.Device_Classes.Devices import Device

from PyQt6.QtWidgets import QWidget
import pyqtgraph as pg


class DiagnosticChannel(QWidget):

    def __init__(self, device: Device):
        super().__init__()
        self.graph = GraphMaker.create(device)
        self.graph.graph.setGeometry(100, 30, 800, 400)
        self.graph.graph.show()

    def update_diagnostic(self):
        pass


if __name__ == "__main__":
    from laser_monitoring.Device_Classes import Devices
    app = pg.mkQApp()
    device_def = dict({("name", "Beam profiler"),
                       ("address", ""),
                       ("type", "dummy device 2D"),
                       ("is virtual", True),
                       ("saving period", 20),
                       ("polling period", 0.1)})

    device = Devices.DeviceMaker.create(device_def)
    print(device)
    diagnostic_channel = DiagnosticChannel(device)
    pg.exec()
