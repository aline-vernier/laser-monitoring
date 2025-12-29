from matplotlib.pyplot import plot
from Graphs.Colours import *
import random
import pyqtgraph as pg


class Dark_StyleSheet():
    """
    Dark Style Sheet for Graphs
    """


    def set_dark_mode(self):
        self.plot.showGrid(x=True, y=True, alpha=0.2)
        self.graph.setBackground(anthracite) 
        self.plot.setContentsMargins(10, 10, 10, 10)

        self.plot.getAxis('bottom').setGrid(128)  # Grid opacity
        self.plot.getAxis('left').setGrid(128)
        # Style the axes with light grey
        axis_pen = pg.mkPen(color=mouse_grey, width=1.5)
        self.plot.getAxis('bottom').setPen(axis_pen)
        self.plot.getAxis('left').setPen(axis_pen)
        self.plot.getAxis('bottom').setTextPen(silver)
        self.plot.getAxis('left').setTextPen(silver)
        
        pen_colour = random.choice(curve_colours)
        self.pen = pg.mkPen(color=pen_colour, width=2)
        self.curve = self.plot.plot(pen=self.pen)    

    def set_labels(self):
        label_style = {'color': silver, 'font-size': '10pt', 'font-family': 'Sergoe UI'}
        self.plot.setLabel('bottom', self.x_label, units=self.x_units, **label_style)
        self.plot.setLabel('left', self.y_label, units=self.y_units, **label_style)  

    def set_2D_plot_darkstyle(self):
        self.graph.setBackground(anthracite) 
        # Color map for 2D plots
        self.plot.addColorBar(self.img_item, colorMap='viridis') 
        self.plot.vb.setAspectLocked(True, 1)


