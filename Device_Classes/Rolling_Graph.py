#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025/12/26
@author: Aline Vernier
Rolling Graph Device Class
"""

from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QFont
import pyqtgraph as pg
import numpy as np
from collections import deque, namedtuple

class Rolling_Graph(QWidget):
    def __init__(self):
        super().__init__()

    graph_widget = pg.GraphicsLayoutWidget()

    # Create the plot
    plot = graph_widget.addPlot()
    plot.setContentsMargins(10, 10, 10, 10)