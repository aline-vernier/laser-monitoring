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

sepa = os.sep


class Monitoring_Interface(QMainWindow):

    def __init__(self):
        super().__init__()
        p = pathlib.Path(__file__)
        self.icon = str(p.parent.parent) + sepa + 'icons' + sepa
        self.setup()
        self._cache_setup()
        self.action_button()

    def setup(self):
        #####################################################################
        #                   Window setup
        #####################################################################
        self.isWinOpen = False
        self.setWindowTitle('Laser Monitoring')
        self.setWindowIcon(QIcon(self.icon + 'LOA.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setGeometry(100, 30, 1200, 750)

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
        b0 = QLabel('')
        b1 = QLabel('')
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
        title_label = QLabel('Laser monitoring')
        title_label.setFont(QFont('Arial', 14))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vbox2.addWidget(title_label)

        #####################################################################
        #       Fill layout with graphs, controls and indicators
        #####################################################################

        ######################
        #       Graphs
        ######################

        # Setup 1D plot
        self.graph_widget = pg.GraphicsLayoutWidget()
        self.vbox1.addWidget(self.graph_widget)

        self.dnde_image = self.graph_widget.addPlot()
        self.dnde_image.setContentsMargins(10, 10, 10, 10)

        self.vbox2.addStretch(1)
        #####################################################################
        #                       Interface actions
        #####################################################################
    def _cache_setup(self):
        pass
    def action_button(self) -> None:
        pass

    def clear_bounds_cache(self):
        pass

    def clear_graph(self) -> None:
        pass

if __name__ == "__main__":

    appli = QApplication(sys.argv)
    appli.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    e=Monitoring_Interface()
    e.show()
    appli.exec_()
