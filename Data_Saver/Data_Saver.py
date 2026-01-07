import h5_Builder
import Device_Classes
from queue import Queue, Full
import threading
import time
from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal


class DataSaver(QObject):
    """Thread-safe data saver for high-frequency acquisition"""
    
    # Signals for monitoring
    buffer_warning = pyqtSignal(int)  # Emitted when buffer fills up
    data_saved = pyqtSignal(int)      # Emitted after batch write (count)
    
    def __init__(self,filename, batch_size=1000, max_buffer=10000, flush_interval=1.0):
        super().__init__()
        self.filename = filename
        self.batch_size = batch_size
        self.max_buffer = max_buffer
        self.flush_interval = flush_interval  # seconds
        
        # Thread-safe buffer
        self.buffer = Queue(maxsize=max_buffer)
        
        # Control flags
        self.running = False
        self.writer_thread = None
        
        # Statistics
        self.total_saved = 0
        self.dropped_count = 0
        
        # HDF5 file and table
        self.h5_file = h5_Builder.H5Builder('./Data_Saver/realtime_data.h5')
        

    def start(self, devices: dict):
        """Initialize HDF5 file and start writer thread"""
        if self.running:
            return
            
        # Configure HDF5 file
        self.h5_file.create_file(devices= devices)

        
        # Start writer thread
        self.running = True
        self.writer_thread = threading.Thread(target=self._write_loop, daemon=True)
        self.writer_thread.start()
        
        print(f"Data saver started: {self.filename}")
        