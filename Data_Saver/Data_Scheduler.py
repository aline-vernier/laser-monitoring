from PyQt6.QtCore import QTimer


class DataSaveScheduler:
    def __init__(self, save_handler):
        self.save_handler = save_handler
        self.latest_data = {}  # device_id -> latest data point
        self.timers = {}  # device_id -> QTimer

    def register_device(self, device_id: str, saving_period: float):
        """Register a device with its save interval"""
        timer = QTimer()
        timer.timeout.connect(lambda: self._save_if_available(device_id))
        timer.start(saving_period * 1000)
        self.timers[device_id] = timer
        self.latest_data[device_id] = None

    def on_data_received(self, device_id, data):
        """Called when new data arrives from device"""
        # Always update the latest data
        self.latest_data[device_id] = data
        # Your display handler runs here
        # No save logic needed!

    def _save_if_available(self, device_id):
        """Timer callback - saves if data is available"""
        data = self.latest_data.get(device_id)
        if data is not None:
            self.save_handler(device_id, data)
            self.latest_data[device_id] = None  # Optional: clear after save

if __name__ == "__main__":

    def handler():
        print(f'Doing stuff with data')
    # Usage
    scheduler = DataSaveScheduler(handler)
    scheduler.register_device("device_1", 5000)  # Save every 5 seconds

    def on_device_event(device_id, data):
        scheduler.on_data_received(device_id, data)  # Store for periodic save