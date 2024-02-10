from flask import Flask, request, jsonify
import redis

redis_url = "redis://localhost:6379"  
redis_client = redis.from_url(redis_url)

app = Flask(__name__)

@app.route('/devdata', methods=['POST'])
def dev_post():
    # Get JSON data from the request
    data = request.get_json()

    # Perform your processing here. For example, just printing the data.
    print(data)
    dev_hash = f"{data.get('device_id')}"

    for key, value in data.items():       
        redis_client.hset(dev_hash,key, value)

    # Send a response back
    return jsonify({"message": "Data received successfully", "data": data}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
