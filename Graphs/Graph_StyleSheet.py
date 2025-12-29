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
        
        pen_colour = random.choice(curve_colours)
        self.pen = pg.mkPen(color=pen_colour, width=2)
        self.curve = self.plot.plot(pen=self.pen)    

    def set_axes(self):
        self.plot.getAxis('bottom').setGrid(128)  # Grid opacity
        self.plot.getAxis('left').setGrid(128)
        # Style the axes with light grey
        axis_pen = pg.mkPen(color=mouse_grey, width=1.5)
        self.plot.getAxis('bottom').setPen(axis_pen)
        self.plot.getAxis('left').setPen(axis_pen)
        self.plot.getAxis('bottom').setTextPen(silver)
        self.plot.getAxis('left').setTextPen(silver)
        

    def set_labels(self):
        label_style = {'color': silver, 'font-size': '10pt', 'font-family': 'Sergoe UI'}
        self.plot.setLabel('bottom', self.x_label, units=self.x_units, **label_style)
        self.plot.setLabel('left', self.y_label, units=self.y_units, **label_style)  

    def set_2D_plot_darkstyle(self):
        self.graph.setBackground(anthracite) 
        # Color map for 2D plots
        self.plot.addColorBar(self.img_item, colorMap='inferno') 
        self.plot.vb.setAspectLocked(True, 1)

        # Show all four axes
        self.plot.showAxis('top')
        self.plot.showAxis('right')

        # Configure each axis
        for axis_name in ['bottom', 'left', 'top', 'right']:
            axis = self.plot.getAxis(axis_name)
            
            # Make ticks smaller
            axis.setStyle(tickLength=-5)  # Negative = ticks point inward, positive = outward
            
            # Reduce padding between axis and plot
            axis.setStyle(tickTextOffset=3)  # Distance between ticks and labels
            
            # You can also adjust font size for compactness
            axis.setStyle(tickFont=pg.QtGui.QFont("Arial", 8))

        # Optional: hide labels on top/right to avoid redundancy
        self.plot.getAxis('top').setStyle(showValues=False)
        self.plot.getAxis('right').setStyle(showValues=False)

        # Set labels only on bottom and left
        self.plot.setLabel('bottom', 'X Position (mm)')
        self.plot.setLabel('left', 'Y Position (mm)')

        self.plot.getViewBox().setDefaultPadding(0.0)


