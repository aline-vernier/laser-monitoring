import Graphs.Colours as Colours   
import pyqtgraph as pg


class Dark_StyleSheet:
    """
    Dark Style Sheet for Graphs
    """
    def set_dark_mode(self):
        self.plot.showGrid(x=True, y=True, alpha=0.2)
        self.graph.setBackground('#1e1e1e') 

        self.plot.getAxis('bottom').setGrid(128)  # Grid opacity
        self.plot.getAxis('left').setGrid(128)
        # Style the axes with light grey
        axis_pen = pg.mkPen(color='#666666', width=1.5)
        self.plot.getAxis('bottom').setPen(axis_pen)
        self.plot.getAxis('left').setPen(axis_pen)
        self.plot.getAxis('bottom').setTextPen('#cccccc')
        self.plot.getAxis('left').setTextPen('#cccccc')
        self.curve = self.plot.plot(pen=pg.mkPen(color=Colours.muted_blue, width=2))    


    def set_labels(self):
        label_style = {'color': '#cccccc', 'font-size': '10pt', 'font-family': 'Sergoe UI'}
        self.plot.setLabel('bottom', self.x_label, units=self.x_units, **label_style)
        self.plot.setLabel('left', self.y_label, units=self.y_units, **label_style)    