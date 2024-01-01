import threading
import random
import time

class DeviceSimulator:
    def __init__(self, seed, interval=1):
        # Initialize the random generator with the seed
        self.random = random.Random(seed)
        self.interval = interval  # Data reporting interval in seconds

    def generate_data(self):
        # Simulate temperature and pressure readings
        temperature = self.random.uniform(-10, 40)  # Range from -10 to 40 degrees
        pressure = self.random.uniform(950, 1050)   # Range from 950 to 1050 hPa
        fan_status = self.random.choice(['on', 'off'])
        pump_status = self.random.choice(['on', 'off'])
        return {
            "temperature": temperature,
            "pressure": pressure,
            "fan_status": fan_status,
            "pump_status": pump_status
        }

    def run(self):
        while True:
            data = self.generate_data()
            print(f"Device {threading.current_thread().name}: {data}")
            time.sleep(self.interval)

# Number of devices to simulate
num_devices = 5000

# Create and start threads for each simulated device
threads = []
for i in range(num_devices):
    simulator = DeviceSimulator(seed=i)
    thread = threading.Thread(target=simulator.run, name=f"Device_{i}")
    thread.start()
    threads.append(thread)

# This simulation will run indefinitely. You can modify the code to stop after a certain period.
# Note: The print statements might not be well-ordered due to the nature of threading.
