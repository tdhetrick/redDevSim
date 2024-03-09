import math
import threading
import random
import time

import requests



url = 'http://127.0.0.1:5000/devdata'

threads = []
num_devices = 4000

class DeviceSimulatorModified:
    def __init__(self, seed, interval=5):
        self.start_interval = interval
        self.random = random.Random(seed)
        self.interval = interval
        # Modifying frequency and amplitude based on the seed
        self.frequency = self.random.uniform(0.1, 1.0)  # Frequency of the sine wave
        self.amplitude = self.random.uniform(5, 20)     # Amplitude of the sine wave
        self.time = 0  # Time variable to simulate continuous time passage

    def generate_data(self):

        # add a little uncertainty to device response
        wait_time = random.randint(1, 5)
        time.sleep(wait_time)
        
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
            try:
                data = self.generate_data()
            except Exception as e:
                print(f"Error generating data: {e}")
                # Handle the error or continue to the next iteration
                continue

            device_name = threading.current_thread().name
            #print(f"Device {device_name}: {data}")

            data['device_id'] = device_name

            try:
                response = requests.post(url, json=data, timeout=5)  # Make sure 'url' is defined
                #response.raise_for_status()  # This will raise an HTTPError if the response was an unsuccessful status code
                if response.elapsed.total_seconds() > 1:
                    self.interval = self.interval * 2
                    print(f"Response time {response.elapsed.total_seconds()} interval now {self.interval }")
            except requests.exceptions.HTTPError as e:
                print(f"HTTP error occurred: {e}")
                # Handle HTTP-specific errors or log them
            except requests.exceptions.ConnectionError as e:
                print(f"Error connecting: {e}")
                self.interval = self.interval * 2
                print(f"INTERVAL CHANGE to {self.interval}")
                # Handle connection errors
            except requests.exceptions.Timeout as e:
                print(f"Timeout error: {e}")
                self.interval = self.interval * 2
                print(f"INTERVAL CHANGE to {self.interval}")
                # Handle requests timeout
            except requests.exceptions.RequestException as e:
                print(f"Error making the request: {e}")
                # Handle any other requests-related errors
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                # Handle any other unexpected errors

            if self.interval > self.start_interval:
                self.interval = self.interval - 1

            time.sleep(self.interval)  # Make sure 'self.interval' is defined
# Restarting the threads with the modified simulator
for thread in threads:  # Stopping the previous threads
    thread.do_run = False


for i in range(num_devices):
    simulator = DeviceSimulatorModified(seed=i)
    thread = threading.Thread(target=simulator.run, name=f"Device_{i}")
    thread.start()
    threads.append(thread)

# This will output data based on sine wave patterns, with each device having its unique pattern.
