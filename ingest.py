from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error, pooling
import json
from datetime import datetime
import threading
import time
import sys, os

flask_pid = os.getpid()
# MySQL connection pool setup
pool_name = "mypool"
pool_size = 16
db_config = {
    "host": "192.168.100.4",
    "database": "devsim",
    "user": "root",
    "password": "4500Creemore",
    "pool_name": pool_name,
    "pool_size": pool_size
}

# Initialize connection pool
try:
    cnx_pool = mysql.connector.pooling.MySQLConnectionPool(pool_reset_session=True, **db_config)
except Error as e:
    print(f"Error creating MySQL pool: {e}")

app = Flask(__name__)

# Initialize a buffer for accumulating data
data_buffer = []
buffer_lock = threading.Lock()


def insert_bulk_data_async(device_data_list):
    try:
        cnx = cnx_pool.get_connection()
        if cnx.is_connected():
            start_time = time.time()
            db_cursor = cnx.cursor()
            values_placeholder = ",".join(["(%s, %s, %s)"] * len(device_data_list))
            query = f"""INSERT INTO device_history (device, ts, data) VALUES {values_placeholder}"""
            flattened_values = [item for sublist in device_data_list for item in sublist]

            # Estimate the size of the data being inserted
            data_size_bytes = sum(sys.getsizeof(value) for value in flattened_values)
            data_size_kilobits = data_size_bytes * 0.008

           

            db_cursor.execute(query, flattened_values)
            cnx.commit()

            elapsed_time = time.time() - start_time

            # Calculate the data transfer rate in kilobits per second
            if elapsed_time > 0:  # Prevent division by zero
                transfer_rate_kbps = data_size_kilobits / elapsed_time
                print(f"Data transfer rate: {transfer_rate_kbps:.2f} kbps from Flask instance {flask_pid}")
            else:
                print("Elapsed time is too short to calculate a meaningful transfer rate.")

            print(f"Bulk data inserted successfully. Elapsed time: {elapsed_time:.4f} seconds")

            db_cursor.close()
            cnx.close()
    except Error as e:
        print(f"Error in async insert: {e}")




def check_and_insert_data(device, ts, data_json):
    global data_buffer
    with buffer_lock:
        data_buffer.append((device, ts, data_json))
        if len(data_buffer) >= 400:
            # Copy buffer and clear it
            temp_buffer = data_buffer[:]
            data_buffer = []
            # Use a separate thread to perform the bulk insert asynchronously
            insert_thread = threading.Thread(target=insert_bulk_data_async, args=(temp_buffer,))
            insert_thread.start()

@app.route('/devdata', methods=['POST'])
def dev_post():
    data = request.get_json()
    device_id = data.get('device_id')
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_json = json.dumps(data)
    
    # Asynchronously check buffer and insert data if necessary
    check_and_insert_data(device_id, ts, data_json)
    print(".",end='')
    # Immediately respond to the client
    return jsonify({"message": "Data received and will be processed"}), 202

if __name__ == '__main__':
    app.run(debug=True, port=5000)
