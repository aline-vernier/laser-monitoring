from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSlot

class ThreadRunAcq(QtCore.QThread):
    """
    Thread for independent asynchronous acquisition
    """
    newDataRun = QtCore.pyqtSignal(object)
    newState = QtCore.pyqtSignal(bool)

    def __init__(self, parent):

        super(ThreadRunAcq, self).__init__()
        self.parent = parent
        self.stopRunAcq = False

    def new_run(self):
        self.stopRunAcq = False

    @pyqtSlot()
    def run(self):
        self.newState.emit(True)
        while self.stopRunAcq is not True:
            try:
                pass
            except:
                pass
        if self.stopRunAcq == True:
            pass

    def stopThreadRunAcq(self):
        self.stopRunAcq = True
