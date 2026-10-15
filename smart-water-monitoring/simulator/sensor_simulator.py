"""
Smart Water Quality Monitoring - Sensor Simulator
=================================================
Simulates 3 water tanks generating sensor data every 5 seconds.
Publishes data via MQTT to Mosquitto broker.

Environment Variables:
    MQTT_BROKER: MQTT broker hostname (default: mosquitto)
    MQTT_PORT: MQTT broker port (default: 1883)
    SIMULATION_INTERVAL: Seconds between readings (default: 5)
"""

import json
import time
import random
import os
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

# ============================================
# Configuration from Environment Variables
# ============================================
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
SIMULATION_INTERVAL = int(os.getenv('SIMULATION_INTERVAL', '5'))

# ============================================
# Tank Definitions - Base values for each tank
# ============================================
TANKS = {
    'TANK001': {
        'pH_base': 7.0,
        'turbidity_base': 2.0,
        'temperature_base': 27.0,
        'waterLevel_base': 75.0
    },
    'TANK002': {
        'pH_base': 7.5,
        'turbidity_base': 1.5,
        'temperature_base': 25.0,
        'waterLevel_base': 85.0
    },
    'TANK003': {
        'pH_base': 6.8,
        'turbidity_base': 3.0,
        'temperature_base': 30.0,
        'waterLevel_base': 60.0
    }
}

# ============================================
# Abnormal Scenarios for Demonstration
# ============================================
ABNORMAL_SCENARIOS = [
    {'name': 'high_pH', 'param': 'pH', 'range': (10.0, 12.0)},
    {'name': 'low_pH', 'param': 'pH', 'range': (2.0, 4.0)},
    {'name': 'high_turbidity', 'param': 'turbidity', 'range': (12.0, 20.0)},
    {'name': 'high_temperature', 'param': 'temperature', 'range': (42.0, 50.0)},
    {'name': 'low_water_level', 'param': 'waterLevel', 'range': (2.0, 8.0)},
    {'name': 'warning_pH', 'param': 'pH', 'range': (9.0, 9.5)},
    {'name': 'warning_turbidity', 'param': 'turbidity', 'range': (6.0, 9.0)},
]


def generate_sensor_data(tank_id, tank_config, abnormal=None):
    """
    Generate simulated sensor data for a water tank.
    
    Args:
        tank_id: Tank identifier (e.g., 'TANK001')
        tank_config: Dict with base values for the tank
        abnormal: Optional dict with abnormal scenario to apply
    
    Returns:
        Dict with sensor readings
    """
    # Generate normal readings with small random variations
    pH = round(tank_config['pH_base'] + random.uniform(-0.3, 0.3), 2)
    turbidity = round(tank_config['turbidity_base'] + random.uniform(-0.5, 0.5), 2)
    temperature = round(tank_config['temperature_base'] + random.uniform(-1.5, 1.5), 1)
    waterLevel = round(tank_config['waterLevel_base'] + random.uniform(-3.0, 3.0), 1)
    
    # Apply abnormal scenario if specified
    if abnormal:
        param = abnormal['param']
        low, high = abnormal['range']
        value = round(random.uniform(low, high), 2)
        if param == 'pH':
            pH = value
        elif param == 'turbidity':
            turbidity = value
        elif param == 'temperature':
            temperature = round(value, 1)
        elif param == 'waterLevel':
            waterLevel = round(value, 1)
    
    # Clamp values to valid ranges
    pH = max(0, min(14, pH))
    turbidity = max(0, turbidity)
    temperature = max(-10, min(60, temperature))
    waterLevel = max(0, min(100, waterLevel))
    
    return {
        'tankId': tank_id,
        'pH': pH,
        'turbidity': turbidity,
        'temperature': temperature,
        'waterLevel': waterLevel,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback when connected to MQTT broker."""
    if rc == 0:
        print("[MQTT] Connected to MQTT broker successfully")
    else:
        print(f"[MQTT] Connection failed with code: {rc}")


def on_disconnect(client, userdata, disconnect_flags, rc=None, properties=None):
    """Callback when disconnected from MQTT broker."""
    if rc != 0 and rc is not None:
        print(f"[MQTT] Unexpected disconnection (code: {rc}). Will auto-reconnect...")


def connect_mqtt():
    """
    Create and connect MQTT client with retry logic and localhost fallback.
    
    Returns:
        Connected MQTT client
    """
    unique_client_id = f"sensor-simulator-{random.randint(1000, 9999)}"
    # Handle paho-mqtt v1 vs v2 compatibility
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=unique_client_id)
    except AttributeError:
        client = mqtt.Client(client_id=unique_client_id, clean_session=True)
        
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    brokers_to_try = [MQTT_BROKER]
    if MQTT_BROKER != 'localhost' and MQTT_BROKER != '127.0.0.1':
        brokers_to_try.append('localhost')

    # Retry connection until successful
    while True:
        for broker in brokers_to_try:
            try:
                print(f"[MQTT] Connecting to {broker}:{MQTT_PORT}...")
                client.connect(broker, MQTT_PORT, keepalive=60)
                client.loop_start()
                time.sleep(2)  # Wait for connection
                return client
            except Exception as e:
                print(f"[MQTT] Connection to {broker} failed: {e}")
        
        print("[MQTT] Retrying connection in 5 seconds...")
        time.sleep(5)


def main():
    """Main simulator loop."""
    # Print startup banner
    print("="*60)
    print("  Smart Water Quality Monitoring - Sensor Simulator")
    print("="*60)
    print(f"  MQTT Broker : {MQTT_BROKER}:{MQTT_PORT}")
    print(f"  Interval    : {SIMULATION_INTERVAL} seconds")
    print(f"  Tanks       : {', '.join(TANKS.keys())}")
    print(f"  Topics      : water/tank/{{tankId}}/sensors")
    print("="*60)
    print()
    
    # Connect to MQTT
    client = connect_mqtt()
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            abnormal_tank = None
            abnormal_scenario = None
            
            # Every 6th iteration (~30 seconds), inject an abnormal reading
            if iteration % 6 == 0:
                abnormal_tank = random.choice(list(TANKS.keys()))
                abnormal_scenario = random.choice(ABNORMAL_SCENARIOS)
                print(f"\n[ABNORMAL] Injecting '{abnormal_scenario['name']}' into {abnormal_tank}")
            
            # Generate and publish data for each tank
            for tank_id, tank_config in TANKS.items():
                # Apply abnormal scenario only to the selected tank
                scenario = abnormal_scenario if tank_id == abnormal_tank else None
                
                # Generate sensor data
                data = generate_sensor_data(tank_id, tank_config, scenario)
                
                # Publish to MQTT
                topic = f"water/tank/{tank_id}/sensors"
                payload = json.dumps(data)
                result = client.publish(topic, payload, qos=1)
                
                # Log the published message
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                status_marker = " [ABNORMAL]" if scenario else ""
                print(f"[{timestamp}] Published to {topic}{status_marker}: {payload}")
            
            print()  # Blank line between iterations
            time.sleep(SIMULATION_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n[INFO] Simulator stopped by user")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[INFO] MQTT client disconnected")


if __name__ == '__main__':
    main()
