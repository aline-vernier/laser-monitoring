from Data_Saver.h5_Builder import H5Builder
from queue import Queue, Full
import threading
import time
from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal
import numpy as np


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
        self.h5_file = H5Builder('./Data_Saver/realtime_data.h5')
        

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

    def stop(self):
        """Stop writer thread and close file"""
        if not self.running:
            return
            
        self.running = False
        
        # Wait for writer thread to finish
        if self.writer_thread:
            self.writer_thread.join(timeout=5.0)
        
        # Flush any remaining data
        self._flush_buffer()
        
            
        print(f"Data saver stopped. Saved: {self.total_saved}, Dropped: {self.dropped_count}")
        
    @pyqtSlot(float, int, int)
    @pyqtSlot(object)
    def on_data_event(self, *args):
        """
        Fast event handler - just adds data to buffer
        
        Can be called as:
        - on_data_event(timestamp, device_id, value)
        - on_data_event((timestamp, device_id, value))
        - on_data_event({'timestamp': t, 'device_id': c, 'value': v})
        """
        if not self.running:
            return
            
        # Parse arguments
        if len(args) == 1:
            data = args[0]
            if isinstance(data, dict):
                data_point = (data['timestamp'], data['device_id'], data['value'])              
            else:
                data_point = data
        else:
            data_point = args
       
        # Try to add to buffer (non-blocking)
        try:
            self.buffer.put_nowait(data_point)
        except Full:
            # Buffer is full - drop the data point
            self.dropped_count += 1
            
            # Emit warning if buffer is consistently full
            if self.dropped_count % 100 == 1:
                self.buffer_warning.emit(self.buffer.qsize())

    def _write_loop(self):
        """Background thread that writes batches to disk"""
        batch = []
        last_flush = time.time()
        
        while self.running or not self.buffer.empty():
            # Collect data points into a batch
            try:
                # Use timeout to periodically check running flag
                data = self.buffer.get(timeout=0.1)
                batch.append(data)
                
            except:
                pass  # Timeout - continue to check if we should flush
                
            # Write batch if it's large enough or enough time has passed
            self.current_time = time.time()
            self.should_flush = (
                len(batch) >= self.batch_size or
                (batch and self.current_time - last_flush >= self.flush_interval)
            )
            
            if self.should_flush:
                self._write_batch(batch)
                batch.clear()
                last_flush = self.current_time
                
        # Write any remaining data
        if batch:
            self._write_batch(batch)

    def _write_batch(self, batch):
        """Write a batch of data points to HDF5"""
        print(f'batch: {batch}')
        if not batch or self.h5_file is None:
            print("No data to write or h5 file not initialized.")
            return
            
        # Convert batch to numpy structured array for efficient writing
        for timestamp, device_id, value in batch:
            data = np.array([timestamp, value])
            self.h5_file.append_batch(device_id, data)
            
    
        self.total_saved += len(batch)
        self.data_saved.emit(len(batch))
        
    def _flush_buffer(self):
        """Flush all remaining data in buffer"""
        batch = []
        while not self.buffer.empty():
            try:
                batch.append(self.buffer.get_nowait())
            except:
                break
                
        if batch:
            self._write_batch(batch)