import tables
import numpy as np
from queue import Queue, Full
import threading
import time
from datetime import datetime
from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal


class DataPoint(tables.IsDescription):
    """Define the structure of each data point in the HDF5 table"""
    timestamp = tables.Float64Col()  # Unix timestamp
    channel = tables.Int16Col()      # Channel/device ID
    value = tables.Int16Col()        # 16-bit measurement value


class DataSaver(QObject):
    """Thread-safe data saver for high-frequency acquisition"""
    
    # Signals for monitoring
    buffer_warning = pyqtSignal(int)  # Emitted when buffer fills up
    data_saved = pyqtSignal(int)      # Emitted after batch write (count)
    
    def __init__(self, filename, batch_size=1000, max_buffer=10000, flush_interval=1.0):
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
        self.h5file = None
        self.table = None
        
    def start(self):
        """Initialize HDF5 file and start writer thread"""
        if self.running:
            return
            
        # Open HDF5 file
        self.h5file = tables.open_file(self.filename, mode='w', title='Acquisition Data')
        
        # Create table with compression
        filters = tables.Filters(complevel=5, complib='zlib')
        self.table = self.h5file.create_table(
            '/', 'measurements', DataPoint,
            'Measurement Data',
            filters=filters,
            expectedrows=10000000  # Optimize for large datasets
        )
        
        # Add metadata
        self.table.attrs.start_time = datetime.now().isoformat()
        
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
        
        # Close HDF5 file
        if self.h5file:
            self.table.attrs.end_time = datetime.now().isoformat()
            self.table.attrs.total_points = self.total_saved
            self.table.attrs.dropped_points = self.dropped_count
            self.h5file.close()
            
        print(f"Data saver stopped. Saved: {self.total_saved}, Dropped: {self.dropped_count}")
        
    @pyqtSlot(float, int, int)
    @pyqtSlot(object)
    def on_data_event(self, *args):
        """
        Fast event handler - just adds data to buffer
        
        Can be called as:
        - on_data_event(timestamp, channel, value)
        - on_data_event((timestamp, channel, value))
        - on_data_event({'timestamp': t, 'channel': c, 'value': v})
        """
        if not self.running:
            return
            
        # Parse arguments
        if len(args) == 1:
            data = args[0]
            if isinstance(data, dict):
                data_point = (data['timestamp'], data['channel'], data['value'])
                
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
        if not batch or self.table is None:
            print("No data to write or table not initialized.")
            return
            
        # Convert batch to numpy structured array for efficient writing
        row = self.table.row
        for timestamp, channel, value in batch:
            row['timestamp'] = timestamp
            row['channel'] = channel
            row['value'] = value
            row.append()
            
        self.table.flush()
    
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
            
    def get_stats(self):
        """Return current statistics"""
        return {
            'total_saved': self.total_saved,
            'dropped': self.dropped_count,
            'buffer_size': self.buffer.qsize(),
            'buffer_percent': (self.buffer.qsize() / self.max_buffer) * 100
        }


# Example usage
if __name__ == '__main__':
    from PyQt6.QtCore import QTimer, QCoreApplication
    import sys
    import random
    
    app = QCoreApplication(sys.argv)
    
    # Create data saver
    saver = DataSaver('./Data_Saver/test_acquisition.h5', batch_size=3, flush_interval=0.5)
    
    # Connect monitoring signals
    saver.buffer_warning.connect(lambda size: print(f"WARNING: Buffer filling up! Size: {size}"))
    saver.data_saved.connect(lambda count: print(f"Saved batch of {count} points"))
    
    saver.start()
    
    # Simulate 100 Hz data acquisition
    call_count = [0]
    def simulate_data():
        call_count[0] += 1
        timestamp = time.time()
        channel = random.randint(0, 10)
        value = random.randint(-32768, 32767)
        saver.on_data_event(timestamp, channel, value)
        if call_count[0] % 100 == 0:
            print(f"Generated {call_count[0]} data points")
    
    timer = QTimer()
    timer.timeout.connect(simulate_data)
    timer.start(3)  # ~300 Hz (every 3ms)
    
    # Stop after 5 seconds
    QTimer.singleShot(5000, lambda: [timer.stop(), saver.stop(), app.quit()])
    
    # Print stats periodically
    def print_stats():
        stats = saver.get_stats()
        print(f"Stats: {stats}")
    
    stats_timer = QTimer()
    stats_timer.timeout.connect(print_stats)
    stats_timer.start(2000)
    
    sys.exit(app.exec())