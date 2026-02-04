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
import PyQt6.QtGui as QtGui
from PyQt6.QtGui import QIcon, QFont, QAction
from PyQt6.QtCore import Qt
import sys
import qdarkstyle
import os
import pathlib
import Graphs.Graph_Maker
from Graphs.Graph_Maker import GraphUpdater
from Device_Classes.Devices import Device 

from SubMenus.WinOption import OPTION

sepa = os.sep


class Monitoring_Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        p = pathlib.Path(__file__)
        self.icon = str(p.parent / 'icons')
        print(f'Icon path: {self.icon + "/LOA.png"}')
        self.name = "VISU"
        self.setup_interface()
        self.setup_button_actions()
        self.graphs = {}
        self.graph_widgets = {}
        

    def setup_interface(self):
        #####################################################################
        #                   Window setup
        #####################################################################
        self.setWindowTitle('Laser Monitoring')
        self.setWindowIcon(QIcon(self.icon + "/LOA.png"))
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        #self.setGeometry(100, 30, 1200, 500)

        self.toolBar = self.addToolBar('tools')
        self.toolBar.setMovable(False)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.fileMenu = self.menuBar().addMenu('&File')
        self.winOpt = OPTION(conf=None, name=self.name, parent=self)
        self.optionAutoSaveAct = QAction(QtGui.QIcon(self.icon+"Settings.png"),
                                         'Options', self)

        
        self.toolBar.addAction(self.optionAutoSaveAct)
        self.fileMenu.addAction(self.optionAutoSaveAct)
        self.optionAutoSaveAct.triggered.connect(
            lambda: self.open_widget(self.winOpt))
        
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

        # Vertical box with stacked 0D graphs
        self.vbox1 = QVBoxLayout()
        self.vbox1.setSpacing(0)
        self.vbox1.setContentsMargins(0, 0, 0, 0)
        self.hbox.addLayout(self.vbox1)

        # Vertical box with stacked 1D and 2D graph
        self.vbox2 = QVBoxLayout()
        self.vbox2.setSpacing(0)
        self.vbox2.setContentsMargins(0, 0, 0, 0)
        self.hbox.addLayout(self.vbox2)

        # Vertical box with controls and indicators
        self.vbox3 = QVBoxLayout()
        self.vbox3.setSpacing(0)
        self.vbox3.setContentsMargins(0, 0, 0, 0)
        self.hbox.addLayout(self.vbox3)

        ######################
        #    Graph controls
        ######################

        grid_layout_graph_functions = QGridLayout()
        graph_settings = QLabel('Graph settings')
        self.clear_graphs_ctl = QPushButton(text="Clear Graphs")
        grid_layout_graph_functions.addWidget(graph_settings, 0, 0)
        grid_layout_graph_functions.addWidget(self.clear_graphs_ctl, 1, 0)
        self.vbox3.addLayout(grid_layout_graph_functions)
        self.vbox3.addStretch(1)

    def setup_button_actions(self):
        self.clear_graphs_ctl.clicked.connect(self.clear_graphs)

    def open_widget(self, win):
        """ open new widget
        """
        if win.isWinOpen is False:
            win.setup
            win.isWinOpen = True
            win.show()
        else:
            win.showNormal()

    ############################################
    #                   Graphs
    ############################################

    def add_graph(self, device: Device):
        graph = Graphs.Graph_Maker.GraphMaker.create(device)    
        self.graphs[device.name] = graph
        if type(graph) is Graphs.Graph_Maker.RollingGraph:
            self.vbox1.addWidget(graph.graph)
            self.vbox1.setSpacing(0)

        else:
            self.vbox2.addWidget(graph.graph)
            self.vbox2.setSpacing(0)
        self.graph_widgets[device.name] = graph.graph 

    def add_stretch(self):
        self.vbox1.addStretch(1)  

    def update_graph(self, device: Device, data: dict):
        graph = self.graphs.get(device.name)
        if graph:
            GraphUpdater(graph).update(data)
        else:
            print(f"Warning: No graph found for device '{device.name}'")

    def clear_graphs(self):
        for device_id, graph in self.graphs.items():
            graph.clear_graph()



if __name__ == "__main__":

    appli = QApplication(sys.argv)   
    e= Monitoring_Interface()
    e.show()
    appli.exec_()
