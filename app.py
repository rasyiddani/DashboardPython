# app.py
from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Create data folder if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Initialize JSON files if they don't exist
def initialize_json_file(file_path, initial_data=None):
    if not os.path.exists(file_path):
        if initial_data is None:
            initial_data = []
        with open(file_path, 'w') as f:
            json.dump(initial_data, f)

# Initialize LED status JSON
led_file = 'data/data_led.json'
initialize_json_file(led_file, [
    {"led1": False, "led2": False, "led3": False, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
])

# Initialize sensor data JSON files
dht22_file = 'data/data_dht22.json'
mq2_file = 'data/data_mq2.json'
initialize_json_file(dht22_file, [])
initialize_json_file(mq2_file, [])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/led/status', methods=['GET'])
def get_led_status():
    try:
        with open(led_file, 'r') as f:
            data = json.load(f)
            if data:
                return jsonify(data[-1])  # Return the latest status
            return jsonify({"led1": False, "led2": False, "led3": False, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/led/toggle', methods=['POST'])
def toggle_led():
    try:
        data = request.get_json()
        led_name = data.get('led')
        status = data.get('status')
        
        with open(led_file, 'r') as f:
            led_data = json.load(f)
        
        # Get the current status (last item)
        current_status = led_data[-1].copy() if led_data else {"led1": False, "led2": False, "led3": False}
        
        # Update the status
        if led_name in ['led1', 'led2', 'led3']:
            current_status[led_name] = status
            current_status['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add new status to the list
            led_data.append(current_status)
            
            # Keep only the last 20 entries
            if len(led_data) > 20:
                led_data = led_data[-20:]
            
            # Save the updated data
            with open(led_file, 'w') as f:
                json.dump(led_data, f)
            
            return jsonify({"success": True, "status": current_status})
        else:
            return jsonify({"error": "Invalid LED name"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sensor/dht22', methods=['POST'])
def update_dht22():
    try:
        data = request.get_json()
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        
        if temperature is None or humidity is None:
            return jsonify({"error": "Missing temperature or humidity data"}), 400
        
        # Read current data
        with open(dht22_file, 'r') as f:
            sensor_data = json.load(f)
        
        # Add new reading
        new_reading = {
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        sensor_data.append(new_reading)
        
        # Keep only the last 20 entries
        if len(sensor_data) > 20:
            sensor_data = sensor_data[-20:]
        
        # Save the updated data
        with open(dht22_file, 'w') as f:
            json.dump(sensor_data, f)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sensor/mq2', methods=['POST'])
def update_mq2():
    try:
        data = request.get_json()
        gas_value = data.get('gas_value')
        
        if gas_value is None:
            return jsonify({"error": "Missing gas value data"}), 400
        
        # Read current data
        with open(mq2_file, 'r') as f:
            sensor_data = json.load(f)
        
        # Add new reading
        new_reading = {
            "gas_value": gas_value,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        sensor_data.append(new_reading)
        
        # Keep only the last 20 entries
        if len(sensor_data) > 20:
            sensor_data = sensor_data[-20:]
        
        # Save the updated data
        with open(mq2_file, 'w') as f:
            json.dump(sensor_data, f)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sensor/data', methods=['GET'])
def get_sensor_data():
    try:
        # Read DHT22 data
        with open(dht22_file, 'r') as f:
            dht22_data = json.load(f)
        
        # Read MQ2 data
        with open(mq2_file, 'r') as f:
            mq2_data = json.load(f)
        
        latest_dht22 = dht22_data[-1] if dht22_data else {"temperature": 0, "humidity": 0, "timestamp": "N/A"}
        latest_mq2 = mq2_data[-1] if mq2_data else {"gas_value": 0, "timestamp": "N/A"}
        
        return jsonify({
            "temperature": latest_dht22.get("temperature", 0),
            "humidity": latest_dht22.get("humidity", 0),
            "gas_value": latest_mq2.get("gas_value", 0),
            "dht22_timestamp": latest_dht22.get("timestamp", "N/A"),
            "mq2_timestamp": latest_mq2.get("timestamp", "N/A")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)