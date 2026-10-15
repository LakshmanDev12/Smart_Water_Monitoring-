"""
Eclipse ioFog Edge Processing Microservice
==========================================
Smart Water Quality Monitoring System
Edge Computing Layer: Validates raw sensor streams, applies threshold
analysis, classifies tank status (SAFE/WARNING/UNSAFE), and pushes
processed telemetry to InfluxDB, Eclipse Ditto, and MQTT Alerts.
"""

import os
import json
import time
import requests
import paho.mqtt.client as mqtt

# ============================================================
# Environment Configuration
# ============================================================
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_SUB_TOPIC = os.getenv('MQTT_SUB_TOPIC', 'water/tank/+/sensors')
MQTT_ALERT_TOPIC = os.getenv('MQTT_ALERT_TOPIC', 'water/alerts')

INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'WaterMonitoring')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'water_quality')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'my-super-secret-token-12345')

DITTO_URL = os.getenv('DITTO_URL', 'http://nginx/api/2')

# ============================================================
# Configurable Quality Thresholds
# ============================================================
THRESHOLDS = {
    'pH': {
        'SAFE_MIN': 6.5,
        'SAFE_MAX': 8.5,
        'WARN_MIN': 5.5,
        'WARN_MAX': 9.5
    },
    'turbidity': {
        'SAFE_MAX': 5.0,
        'WARN_MAX': 10.0
    },
    'temperature': {
        'SAFE_MIN': 20.0,
        'SAFE_MAX': 35.0,
        'WARN_MAX': 40.0
    },
    'waterLevel': {
        'SAFE_MIN': 30.0,
        'WARN_MIN': 10.0
    }
}


def validate_sensor_data(data):
    """Edge Step 1: Validate incoming payload completeness and sensor range validity."""
    if not isinstance(data, dict):
        return False, ["Payload must be a JSON object"]

    errors = []
    required_fields = ['tankId', 'pH', 'turbidity', 'temperature', 'waterLevel', 'timestamp']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Value range checks
    if not (0 <= data['pH'] <= 14):
        errors.append(f"pH out of physical range (0-14): {data['pH']}")
    if data['turbidity'] < 0:
        errors.append(f"Turbidity cannot be negative: {data['turbidity']}")
    if not (-50 <= data['temperature'] <= 100):
        errors.append(f"Temperature out of sensor operating range (-50 to 100°C): {data['temperature']}")
    if not (0 <= data['waterLevel'] <= 100):
        errors.append(f"Water level out of percentage range (0-100%): {data['waterLevel']}")

    return (len(errors) == 0), errors


def analyze_and_classify(data):
    """Edge Step 2: Threshold Analysis and SAFE/WARNING/UNSAFE Classification."""
    alerts = []
    param_statuses = []

    # 1. pH Analysis
    pH = data['pH']
    if THRESHOLDS['pH']['SAFE_MIN'] <= pH <= THRESHOLDS['pH']['SAFE_MAX']:
        param_statuses.append('SAFE')
    elif THRESHOLDS['pH']['WARN_MIN'] <= pH <= THRESHOLDS['pH']['WARN_MAX']:
        param_statuses.append('WARNING')
        msg = f"Low pH detected: {pH}" if pH < THRESHOLDS['pH']['SAFE_MIN'] else f"High pH detected: {pH}"
        alerts.append(msg)
    else:
        param_statuses.append('UNSAFE')
        msg = f"CRITICAL: Very low pH: {pH}" if pH < THRESHOLDS['pH']['WARN_MIN'] else f"CRITICAL: Very high pH: {pH}"
        alerts.append(msg)

    # 2. Turbidity Analysis
    turbidity = data['turbidity']
    if turbidity <= THRESHOLDS['turbidity']['SAFE_MAX']:
        param_statuses.append('SAFE')
    elif turbidity <= THRESHOLDS['turbidity']['WARN_MAX']:
        param_statuses.append('WARNING')
        alerts.append(f"High turbidity detected: {turbidity} NTU")
    else:
        param_statuses.append('UNSAFE')
        alerts.append(f"CRITICAL: Very high turbidity: {turbidity} NTU")

    # 3. Temperature Analysis
    temp = data['temperature']
    if THRESHOLDS['temperature']['SAFE_MIN'] <= temp <= THRESHOLDS['temperature']['SAFE_MAX']:
        param_statuses.append('SAFE')
    elif temp <= THRESHOLDS['temperature']['WARN_MAX']:
        param_statuses.append('WARNING')
        msg = f"Low temperature detected: {temp}°C" if temp < THRESHOLDS['temperature']['SAFE_MIN'] else f"High temperature detected: {temp}°C"
        alerts.append(msg)
    else:
        param_statuses.append('UNSAFE')
        alerts.append(f"CRITICAL: Very high temperature: {temp}°C")

    # 4. Water Level Analysis
    level = data['waterLevel']
    if level >= THRESHOLDS['waterLevel']['SAFE_MIN']:
        param_statuses.append('SAFE')
    elif level >= THRESHOLDS['waterLevel']['WARN_MIN']:
        param_statuses.append('WARNING')
        alerts.append(f"Low water level: {level}%")
    else:
        param_statuses.append('UNSAFE')
        alerts.append(f"CRITICAL: Very low water level: {level}%")

    # Overall Status Aggregation
    if 'UNSAFE' in param_statuses:
        overall_status = 'UNSAFE'
    elif 'WARNING' in param_statuses:
        overall_status = 'WARNING'
    else:
        overall_status = 'SAFE'

    return overall_status, alerts


def write_to_influxdb(processed_data):
    """Write processed telemetry in InfluxDB line protocol format."""
    try:
        tank_id = processed_data['tankId']
        status = processed_data['status']
        alerts_str = "; ".join(processed_data['alerts']) if processed_data['alerts'] else "none"

        # Line protocol format:
        # water_quality,tankId=TANK001 pH=7.1,turbidity=2.3,temperature=26.5,waterLevel=75.2,status="SAFE",statusCode=0i,alerts="none"
        status_code = 0 if status == 'SAFE' else (1 if status == 'WARNING' else 2)
        line = (
            f"water_quality,tankId={tank_id} "
            f"pH={processed_data['pH']},"
            f"turbidity={processed_data['turbidity']},"
            f"temperature={processed_data['temperature']},"
            f"waterLevel={processed_data['waterLevel']},"
            f'status="{status}",'
            f"statusCode={status_code}i,"
            f'alerts="{alerts_str}"'
        )

        url = f"{INFLUXDB_URL}/api/v2/write?org={INFLUXDB_ORG}&bucket={INFLUXDB_BUCKET}&precision=ms"
        headers = {
            'Authorization': f'Token {INFLUXDB_TOKEN}',
            'Content-Type': 'text/plain; charset=utf-8'
        }
        res = requests.post(url, data=line, headers=headers, timeout=5)
        return res.status_code
    except Exception as e:
        print(f"[ioFog Edge Processor] InfluxDB Write Error: {e}")
        return None


def update_eclipse_ditto(processed_data):
    """Update Eclipse Ditto Digital Twin features via REST API."""
    try:
        tank_id = processed_data['tankId']
        url = f"{DITTO_URL}/things/water:{tank_id}/features/waterQuality/properties"
        payload = {
            "pH": processed_data['pH'],
            "turbidity": processed_data['turbidity'],
            "temperature": processed_data['temperature'],
            "waterLevel": processed_data['waterLevel'],
            "status": processed_data['status'],
            "alerts": processed_data['alerts'],
            "timestamp": processed_data['timestamp']
        }
        headers = {'Content-Type': 'application/json'}
        res = requests.put(url, json=payload, headers=headers, timeout=5)
        return res.status_code
    except Exception as e:
        print(f"[ioFog Edge Processor] Ditto Update Error: {e}")
        return None


def on_message(client, userdata, msg):
    """MQTT callback executed on incoming sensor message."""
    try:
        raw_payload = msg.payload.decode('utf-8')
        sensor_data = json.loads(raw_payload)

        # 1. Edge Validation
        is_valid, validation_errors = validate_sensor_data(sensor_data)
        if not is_valid:
            print(f"[ioFog Edge Processor] ❌ REJECTED invalid payload on {msg.topic}: {validation_errors}")
            return

        # 2. Edge Threshold Analysis & Status Classification
        status, alerts = analyze_and_classify(sensor_data)

        processed = {
            "tankId": sensor_data['tankId'],
            "pH": sensor_data['pH'],
            "turbidity": sensor_data['turbidity'],
            "temperature": sensor_data['temperature'],
            "waterLevel": sensor_data['waterLevel'],
            "status": status,
            "alerts": alerts,
            "timestamp": sensor_data['timestamp']
        }

        # 3. Publish Edge Alerts if Warning or Unsafe
        if status in ['WARNING', 'UNSAFE']:
            alert_msg = {
                "tankId": processed['tankId'],
                "status": status,
                "message": ", ".join(alerts),
                "alerts": alerts,
                "pH": processed['pH'],
                "turbidity": processed['turbidity'],
                "temperature": processed['temperature'],
                "waterLevel": processed['waterLevel'],
                "timestamp": processed['timestamp']
            }
            client.publish(MQTT_ALERT_TOPIC, json.dumps(alert_msg), qos=1)
            print(f"[ioFog Edge Processor] 🚨 ALERT Published to {MQTT_ALERT_TOPIC}: {alert_msg['message']}")

        # 4. Asynchronous Storage to InfluxDB & Ditto Twin
        influx_status = write_to_influxdb(processed)
        ditto_status = update_eclipse_ditto(processed)

        # 5. Live Console Logging
        status_icon = "✅" if status == "SAFE" else ("⚠️" if status == "WARNING" else "🔴")
        print(f"[ioFog Edge Processor] {status_icon} [{processed['tankId']}] Status: {status:7s} | "
              f"pH={processed['pH']:4.2f}, Turb={processed['turbidity']:4.1f} NTU, "
              f"Temp={processed['temperature']:4.1f}°C, Level={processed['waterLevel']:4.1f}% | "
              f"InfluxDB: {influx_status}, Ditto: {ditto_status}")

    except Exception as ex:
        print(f"[ioFog Edge Processor] Error processing message: {ex}")


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[ioFog Edge Processor] Connected to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_SUB_TOPIC, qos=1)
        print(f"[ioFog Edge Processor] Subscribed to topic: {MQTT_SUB_TOPIC}")
    else:
        print(f"[ioFog Edge Processor] MQTT connection failed with code: {rc}")


def main():
    print("=" * 65)
    print("  🌐 Eclipse ioFog Edge Processing Microservice")
    print("  Smart Water Quality Monitoring & Digital Twin")
    print("=" * 65)
    print(f"  Broker Address   : {MQTT_BROKER}:{MQTT_PORT}")
    print(f"  Telemetry Topic  : {MQTT_SUB_TOPIC}")
    print(f"  Alert Topic      : {MQTT_ALERT_TOPIC}")
    print(f"  InfluxDB Target  : {INFLUXDB_URL} (Org: {INFLUXDB_ORG}, Bucket: {INFLUXDB_BUCKET})")
    print(f"  Ditto API Target : {DITTO_URL}")
    print("=" * 65)

    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="iofog-edge-processor")
    client.on_connect = on_connect
    client.on_message = on_message

    # Reconnect loop until broker is reachable
    while True:
        try:
            print(f"[ioFog Edge Processor] Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}...")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            break
        except Exception as e:
            print(f"[ioFog Edge Processor] Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[ioFog Edge Processor] Shutting down microservice gracefully.")
        client.disconnect()


if __name__ == '__main__':
    main()
