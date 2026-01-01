
import Graphs.Colours as Colours
from Graphs.Graph_StyleSheet import Dark_StyleSheet
from Device_Classes.Devices import Device
import Device_Classes.Devices as Devices

from PyQt6.QtWidgets import QWidget
import pyqtgraph as pg
from collections import deque
from abc import abstractmethod


class Graph(QWidget):
    def __init__(self, device: Device):
        super().__init__()

        self.graph = pg.GraphicsLayoutWidget()
        self.graph.ci.setContentsMargins(5, 5, 5, 5)
        self.plot = self.graph.addPlot()
        
        self.x_label= device.labels.get('x_label', 'Time')
        self.y_label= device.labels.get('y_label', 'Signal')
        self.x_units= device.labels.get('x_units', 's')
        self.y_units= device.labels.get('y_units', 'a.u.')

        self.plot.setTitle(device.name)

    @abstractmethod
    def update_graph(self, data: dict):
        pass


class Rolling_Graph(Graph, Dark_StyleSheet):
    def __init__(self, device: Device):
        super().__init__(device)
        
        self.x = deque(maxlen=1000)
        self.y = deque(maxlen=1000)
        self.set_dark_mode()
        self.set_labels() # From Dark_StyleSheet
   

    def update_graph(self, data: dict):
        x = data.get('x', 0)
        y = data.get('y', 0)
        self.x.append(x)
        self.y.append(y)
        self.curve.setData(list(self.x), list(self.y))

class Static_Graph(Graph, Dark_StyleSheet):
    def __init__(self, device: Device):
        super().__init__(device)
        self.set_dark_mode()
        self.set_axes() # From Dark_StyleSheet
        self.set_labels() # From Dark_StyleSheet
   

    def update_graph(self, data: dict):
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        #self.plot.clear()
        self.curve.setData(list(self.x), list(self.y))

class Density_Graph(Graph, Dark_StyleSheet):
    def __init__(self, device: Device):
        super().__init__(device)
        
        self.img_item = pg.ImageItem()
        self.plot.addItem(self.img_item)
        self.plot.setAspectLocked(True, ratio=1.0)      

        self.set_2D_plot_darkstyle()

    def resize(self, w_h_tuple: tuple): 
        width, height = w_h_tuple
        width = int(width/10)
        height = int(height/10)
        self.plot.setAspectLocked(True, ratio=width/height)
        self.img_item.setRect(0, 0, width, height)
        for axis in ['left', 'bottom', 'right', 'top']:
            self.plot.hideAxis(axis)
          


    def update_graph(self, data: dict):
        image = data.get('image', None)
        if image is not None:
            self.img_item.setImage(image)  # Transpose for correct orientation


class GraphMaker:
    _graph_types = {
        'rolling_1d': Rolling_Graph,
        'static_1d': Static_Graph,
        'density_2d': Density_Graph}

    @classmethod
    def create(cls, device: Device) -> Graph:
        graph_type = device.graph_type
        graph_type_class = cls._graph_types.get(graph_type)         
        if not graph_type_class:
            raise ValueError(f"Unknown graph type: {graph_type}")
        return graph_type_class(device)
    
class GraphUpdater:
    def __init__(self, graph: Graph):
        self.graph = graph
    
    def update(self, data: dict):
        """Update the graph with new data - delegates to graph's own method"""
        self.graph.update_graph(data)

if __name__ == "__main__":
    app = pg.mkQApp()
    device_def = dict({('name', 'Dummy device 1'),
                             ('address', ""),
                             ('type', 'dummy device 2D')})
    device = Devices.DeviceMaker.create(device_def)
    print(device)
    graph = GraphMaker.create(device)
    graph.graph.setGeometry(100, 30, 800, 400)
    graph.graph.show()
    pg.exec()