import math
import threading
import random
import time
import redis

redis_url = "redis://localhost:6379"  
redis_client = redis.from_url(redis_url)

threads = []
num_devices = 50000

class DeviceSimulatorModified:
    def __init__(self, seed, interval=1):
        self.random = random.Random(seed)
        self.interval = interval
        # Modifying frequency and amplitude based on the seed
        self.frequency = self.random.uniform(0.1, 1.0)  # Frequency of the sine wave
        self.amplitude = self.random.uniform(5, 20)     # Amplitude of the sine wave
        self.time = 0  # Time variable to simulate continuous time passage

    def generate_data(self):
        
        sine_value = self.amplitude * math.sin(self.frequency * self.time)

        
        temperature = sine_value + 20  # Offset to avoid negative values
        pressure = 1000 + sine_value

        # Fan turns on at the peak and off at the valley
        fan_status = 'on' if sine_value > 0 else 'off'

        # Pump does the opposite
        pump_status = 'off' if sine_value > 0 else 'on'

        # Increment time
        self.time += self.interval

        return {
            "temperature": temperature,
            "pressure": pressure,
            "fan_status": fan_status,
            "pump_status": pump_status
        }

    def run(self):
        while True:
            data = self.generate_data()
            device_name = threading.current_thread().name
            print(f"Device {threading.current_thread().name}: {data}")
            

            for key, value in data.items():
                redis_key = f"{device_name}:{key}"
                redis_client.set(redis_key, value)

            time.sleep(self.interval)    

# Restarting the threads with the modified simulator
for thread in threads:  # Stopping the previous threads
    thread.do_run = False


for i in range(num_devices):
    simulator = DeviceSimulatorModified(seed=i)
    thread = threading.Thread(target=simulator.run, name=f"Device_{i}")
    thread.start()
    threads.append(thread)

# This will output data based on sine wave patterns, with each device having its unique pattern.
