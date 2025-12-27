#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025/12/16
@author: Aline Vernier
Build Spectrometer Interface - GUI only
"""
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QGridLayout
from PyQt6.QtWidgets import (QLabel, QMainWindow, QStatusBar, QComboBox,
                             QCheckBox, QDoubleSpinBox,  QPushButton, QLineEdit)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
import sys
import pyqtgraph as pg
import qdarkstyle
import os
import pathlib
import numpy as np
import Graphs.Rolling_Graph 

sepa = os.sep


class Monitoring_Interface(QMainWindow):

    def __init__(self, buffer_size: int=1000):
        super().__init__()
        p = pathlib.Path(__file__)
        self.icon = str(p.parent) + sepa + 'icons' + sepa
        print(f'Icon path: {self.icon + "LOA.png"}')
        self.setup_interface()
        self.graphs = {}
        self.graph_widgets = {}

    def setup_interface(self):
        #####################################################################
        #                   Window setup
        #####################################################################
        self.setWindowTitle('Laser Monitoring')
        self.setWindowIcon(QIcon(self.icon + 'LOA.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setGeometry(100, 30, 1200, 500)

        self.toolBar = self.addToolBar('tools')
        self.toolBar.setMovable(False)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.fileMenu = self.menuBar().addMenu('&File')

        #####################################################################
        #                   Global layout and geometry
        #####################################################################

        # Toggle design
        TogOff = self.icon + 'Toggle_Off.png'
        TogOn = self.icon + 'Toggle_On.png'
        TogOff = pathlib.Path(TogOff)
        TogOff = pathlib.PurePosixPath(TogOff)
        TogOn = pathlib.Path(TogOn)
        TogOn = pathlib.PurePosixPath(TogOn)
        self.setStyleSheet("QCheckBox::indicator{width: 30px;height: 30px;}"
                           "QCheckBox::indicator:unchecked { image : url(%s);}"
                           "QCheckBox::indicator:checked { image:  url(%s);}"
                           "QCheckBox{font :10pt;}" % (TogOff, TogOn))

        # Horizontal box with LHS graphs, and RHS controls and indicators
        self.hbox = QHBoxLayout()
        MainWidget = QWidget()
        MainWidget.setLayout(self.hbox)
        self.setCentralWidget(MainWidget)

        # LHS vertical box with stacked graphs
        self.vbox1 = QVBoxLayout()
        self.hbox.addLayout(self.vbox1)

        # RHS vertical box with controls and indicators
        self.vbox2 = QVBoxLayout()
        self.vbox2widget = QWidget()
        self.vbox2widget.setLayout(self.vbox2)
        self.vbox2widget.setFixedWidth(100)
        self.hbox.addWidget(self.vbox2widget)

        # Title
        title_label = QLabel('')
        title_label.setFont(QFont('Arial', 14))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vbox2.addWidget(title_label)


    ############################################
    #                   Graphs
    ############################################

    ######################
    #   Rolling Graph
    ######################

    def add_rolling_graph(self, device_name: str,device_labels: dict):

        rolling_graph = Graphs.Rolling_Graph.Rolling_Graph(device_labels)    
        self.graphs[device_name] =  rolling_graph
        self.vbox1.addWidget(rolling_graph.graph)
        self.graph_widgets[device_name] = rolling_graph.graph
  

    def update_rolling_graph(self, device_name: str, data: dict):
        """Update a specific device's rolling graph"""
        graph = self.graphs.get(device_name)
        if graph:
            graph.update_graph(data)
        else:
            print(f"Warning: No rolling graph found for device '{device_name}'")

    ######################
    #   1D Graph
    ######################

    def get_graph(self, device_name: str):
        """Retrieve a specific graph by device name"""
        pass

    def remove_graph(self, device_name: str):
        """Remove a graph and its widget"""
        pass


if __name__ == "__main__":

    appli = QApplication(sys.argv)   
    e= Monitoring_Interface()
    e.show()
    appli.exec_()
