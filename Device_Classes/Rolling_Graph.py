#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025/12/26
@author: Aline Vernier
Rolling Graph Device Class
"""

from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QFont
import sys
import pyqtgraph as pg
import numpy as np
from collections import deque

class Rolling_Graph(QWidget):

    def __init__(self, labels_units: dict):
        super().__init__()
        
        self.x = deque(maxlen=1000)
        self.y = deque(maxlen=1000)
        self.x_label= labels_units.get('x_label', 'Time')
        self.y_label= labels_units.get('y_label', 'Signal')
        self.x_units= labels_units.get('x_units', 's')
        self.y_units= labels_units.get('y_units', 'a.u.')
        self.graph = pg.GraphicsLayoutWidget()
        self.plot = self.graph.addPlot()
        self.plot.setContentsMargins(10, 10, 10, 10)
        #self.set_labels()
    

    def set_labels(self):
        self.plot.setLabel('bottom', self.x_label, units=self.x_units)  # adjust units
        self.plot.setLabel('left', self.y_label, units=self.y_units)    

    def update_graph(self, data: dict):
        new_x = data.get('x', 0)
        new_y = data.get('y', 0)
        self.x.append(new_x)
        self.y.append(new_y)
        self.plot.clear()
        self.plot.plot(list(self.x), list(self.y), pen=pg.mkPen('b', width=2))



if __name__ == "__main__":
    app = pg.mkQApp()
    labels = {'x_label': 'Time', 'y_label': 'Signal', 'x_units': 's', 'y_units': 'V'}
    graph = Rolling_Graph(labels)
    graph.graph.setGeometry(100, 30, 800, 400)
    graph.graph.show()
    pg.exec()