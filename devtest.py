import threading
import random
import time

class DeviceSimulator:
    def __init__(self, seed, interval=1):
        
        self.random = random.Random(seed)
        self.interval = interval  # Data reporting interval in seconds

    def generate_data(self):
        
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


num_devices = 5000

threads = []
for i in range(num_devices):
    simulator = DeviceSimulator(seed=i)
    thread = threading.Thread(target=simulator.run, name=f"Device_{i}")
    thread.start()
    threads.append(thread)


