# 🌊 Smart Water Quality Monitoring & Digital Twin

A complete IoT-based smart water tank monitoring system using Docker, Python, MQTT, Node-RED, InfluxDB, Grafana, and Eclipse Ditto.

![Architecture](https://img.shields.io/badge/Architecture-IoT%20Edge%20Computing-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

1. [Project Objective](#-project-objective)
2. [System Architecture](#-system-architecture)
3. [Technology Stack](#-technology-stack)
4. [Folder Structure](#-folder-structure)
5. [Prerequisites](#-prerequisites)
6. [Installation & Setup](#-installation--setup)
7. [Docker Commands](#-docker-commands)
8. [MQTT Topics](#-mqtt-topics)
9. [Node-RED Edge Processing](#-node-red-edge-processing)
10. [InfluxDB Configuration](#-influxdb-configuration)
11. [Grafana Dashboard](#-grafana-dashboard)
12. [Eclipse Ditto Digital Twin](#-eclipse-ditto-digital-twin)
13. [Testing Guide](#-testing-guide)
14. [Expected Output](#-expected-output)
15. [Troubleshooting](#-troubleshooting)
16. [Future Enhancements](#-future-enhancements)

---

## 🎯 Project Objective

Build an IoT-based smart water tank monitoring system where:

- A **Python Sensor Simulator** generates realistic water-quality data for 3 tanks
- **Eclipse Mosquitto** transfers data via MQTT protocol
- **Node-RED** acts as the **Edge Computing Layer** performing data validation, threshold analysis, and status classification
- **InfluxDB** stores historical time-series data
- **Grafana** provides real-time dashboards and visualizations
- **Eclipse Ditto** maintains a digital twin of each water tank

---

## 🏗️ System Architecture

```
┌─────────────────────┐
│  Python Sensor      │
│  Simulator          │
│  (3 tanks)          │
└────────┬────────────┘
         │ MQTT Publish
         ▼
┌─────────────────────┐
│  Eclipse Mosquitto  │
│  MQTT Broker        │
│  (Port 1883)        │
└────────┬────────────┘
         │ MQTT Subscribe
         ▼
┌─────────────────────────────────────────┐
│          Node-RED                        │
│       EDGE COMPUTING LAYER               │
│                                          │
│  ┌──────────┐  ┌───────────┐  ┌───────┐ │
│  │Validation│→ │Thresholds │→ │Status │ │
│  │          │  │Analysis   │  │SAFE/  │ │
│  │          │  │           │  │WARN/  │ │
│  │          │  │           │  │UNSAFE │ │
│  └──────────┘  └───────────┘  └───┬───┘ │
│                                   │     │
└───────────────────────────────────┼─────┘
         ┌──────────────────────────┼──────────────┐
         │                          │              │
         ▼                          ▼              ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐
│   InfluxDB      │  │  Eclipse Ditto   │  │  MQTT Alert  │
│   Time-Series   │  │  Digital Twin    │  │  (via REST API)  │  │              │
│   Database      │  │  (Port 8085)     │  │              │
│   (Port 8086)   │  │  (via REST API)  │  │  water/alerts│
└────────┬────────┘  └──────────────────┘  └──────────────┘
         │
         ▼
┌─────────────────┐
│   Grafana       │
│   Dashboard     │
│   (Port 3000)   │
└─────────────────┘
```

### Why Node-RED is the Edge Computing Layer

In real IoT deployments, edge computing processes data close to the source before sending it to the cloud. Node-RED acts as our edge layer because:

1. **Local Processing**: All data validation, threshold analysis, and classification happen inside Node-RED before data reaches the database
2. **Reduced Latency**: Abnormal conditions are detected immediately without round-tripping to a database
3. **Data Filtering**: Invalid sensor data is rejected at the edge, preventing bad data from entering storage
4. **Alert Generation**: Real-time alerts are generated locally without waiting for database queries
5. **Protocol Translation**: Node-RED bridges MQTT (from sensors) to HTTP (for InfluxDB and Ditto)

---

## 🛠️ Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|----------|
| Simulator | Python | 3.11 | Generate sensor data |
| MQTT Broker | Eclipse Mosquitto | 2.x | Message transport |
| Edge Processing | Node-RED | 3.x | Data validation & classification |
| Time-Series DB | InfluxDB | 2.7 | Historical data storage |
| Dashboard | Grafana | 10.2 | Data visualization |
| Digital Twin | Eclipse Ditto | 3.4.3 | Virtual representation of tanks |
| Database | MongoDB | 6.0 | Required by Ditto |
| Reverse Proxy | Nginx | 1.25 | Ditto API gateway |
| Container Runtime | Docker Desktop | Latest | Container orchestration |

---

## 📁 Folder Structure

```
smart-water-monitoring/
├── docker-compose.yml          # All services configuration
├── .env                        # Environment variables
├── README.md                   # This file
│
├── mosquitto/
│   └── config/
│       └── mosquitto.conf      # MQTT broker configuration
│
├── simulator/
│   ├── sensor_simulator.py     # Python sensor simulator
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Simulator container
│
├── nodered/
│   └── data/
│       └── flows.json          # Node-RED edge processing flows
│
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── influxdb.yml    # InfluxDB datasource config
│       └── dashboards/
│           ├── dashboard.yml   # Dashboard provisioning config
│           └── water-quality.json  # Dashboard definition
│
├── ditto/
│   ├── nginx.conf              # Nginx reverse proxy for Ditto
│   ├── setup-ditto.ps1         # Setup script (Windows)
│   └── setup-ditto.sh          # Setup script (Linux/Mac)
│
├── influxdb/                   # InfluxDB data (Docker volume)
└── grafana/                    # Grafana data (Docker volume)
```

---

## ✅ Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- At least **8 GB RAM** available for Docker (Ditto services need memory)
- Ports available: `1883`, `1880`, `8086`, `3000`, `8085`, `9001`

---

## 🚀 Installation & Setup

### Step 1: Clone/Download the Project

```powershell
cd e:\Cloud\smart-water-monitoring
```

### Step 2: Start Core Services First

Start the infrastructure services first (without the simulator):

```powershell
# Start MQTT, Node-RED, InfluxDB, and Grafana
docker compose up -d mosquitto nodered influxdb grafana
```

Wait 30 seconds for services to initialize, then check:

```powershell
docker compose ps
```

### Step 3: Start Ditto Services

```powershell
# Start MongoDB and all Ditto services
docker compose up -d mongodb ditto-policies ditto-things ditto-things-search ditto-gateway ditto-connectivity nginx
```

Wait 60-90 seconds for Ditto to fully initialize (Java services take time).

### Step 4: Setup Digital Twins

Run the setup script to create the digital twin policy and things:

```powershell
# Windows
.\ditto\setup-ditto.ps1

# Linux/Mac
bash ditto/setup-ditto.sh
```

### Step 5: Start the Sensor Simulator

```powershell
docker compose up -d simulator
```

### Step 6: Open Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| Node-RED | http://localhost:1880 | No auth |
| Grafana | http://localhost:3000 | admin / admin |
| InfluxDB | http://localhost:8086 | admin / adminpassword123 |
| Ditto API | http://localhost:8085/api/2/things | No auth (pre-authenticated) |

### All-in-One Start

To start everything at once:

```powershell
docker compose up -d
```

Then wait ~90 seconds and run the Ditto setup script.

---

## 🐳 Docker Commands

```powershell
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Stop and remove all data volumes
docker compose down -v

# View running containers
docker compose ps

# View logs for all services
docker compose logs

# View logs for a specific service
docker compose logs nodered
docker compose logs simulator
docker compose logs mosquitto

# Follow logs in real-time
docker compose logs -f simulator

# Restart a service
docker compose restart nodered

# Rebuild simulator after code changes
docker compose build simulator
docker compose up -d simulator
```

---

## 📡 MQTT Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `water/tank/TANK001/sensors` | Simulator → Mosquitto | Tank 1 sensor data |
| `water/tank/TANK002/sensors` | Simulator → Mosquitto | Tank 2 sensor data |
| `water/tank/TANK003/sensors` | Simulator → Mosquitto | Tank 3 sensor data |
| `water/tank/+/sensors` | Mosquitto → Node-RED | Wildcard subscription |
| `water/alerts` | Node-RED → Mosquitto | Alert notifications |

### Data Format

```json
{
  "tankId": "TANK001",
  "pH": 7.2,
  "turbidity": 2.5,
  "temperature": 28.0,
  "waterLevel": 80.0,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## 🔧 Node-RED Edge Processing

Open Node-RED at **http://localhost:1880** to view and modify the edge processing flow.

### Processing Pipeline

1. **MQTT Input**: Subscribes to `water/tank/+/sensors`
2. **JSON Parse**: Converts incoming MQTT string to JSON object
3. **Data Validation**: Checks for required fields and valid ranges
4. **Threshold Analysis**: Applies configurable thresholds to each parameter
5. **Status Classification**: Determines overall SAFE / WARNING / UNSAFE status
6. **Output Branching**:
   - **InfluxDB**: Writes data in line protocol format via HTTP API
   - **Eclipse Ditto**: Updates digital twin via REST API
   - **MQTT Alert**: Publishes warnings/alerts to `water/alerts` topic

### Threshold Configuration

Thresholds are defined in the "Threshold Analysis & Classification" function node:

| Parameter | SAFE | WARNING | UNSAFE |
|-----------|------|---------|--------|
| pH | 6.5 – 8.5 | 5.5 – 6.5 or 8.5 – 9.5 | < 5.5 or > 9.5 |
| Turbidity (NTU) | 0 – 5 | 5 – 10 | > 10 |
| Temperature (°C) | 20 – 35 | 35 – 40 | > 40 |
| Water Level (%) | ≥ 30 | 10 – 30 | < 10 |

### Status Logic

- **SAFE**: All parameters within safe range
- **WARNING**: One or more parameters in warning range, none unsafe
- **UNSAFE**: Any parameter in unsafe range

### Processed Output Example

```json
{
  "tankId": "TANK001",
  "pH": 7.2,
  "turbidity": 2.5,
  "temperature": 28,
  "waterLevel": 80,
  "status": "SAFE",
  "alerts": [],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## 💾 InfluxDB Configuration

| Setting | Value |
|---------|-------|
| URL | http://localhost:8086 |
| Organization | WaterMonitoring |
| Bucket | water_quality |
| Username | admin |
| Password | adminpassword123 |
| API Token | my-super-secret-token-12345 |

### Data Storage

- **Measurement**: `water_quality`
- **Tag**: `tankId` (for filtering by tank)
- **Fields**: `pH`, `turbidity`, `temperature`, `waterLevel`, `status`, `alerts`

### Query Example (Flux)

```flux
from(bucket: "water_quality")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "water_quality")
  |> filter(fn: (r) => r.tankId == "TANK001")
  |> filter(fn: (r) => r._field == "pH")
```

---

## 📊 Grafana Dashboard

Open Grafana at **http://localhost:3000** (login: admin/admin).

The pre-provisioned dashboard "Smart Water Quality Monitoring" includes:

1. **Current Values Row**: Stat panels showing latest pH, turbidity, temperature, water level, and overall status
2. **Historical Data Row**: Time-series graphs for each parameter over time
3. **Tank Selector**: Dropdown to filter by TANK001, TANK002, or TANK003

The dashboard auto-refreshes every 5 seconds.

---

## 🔗 Eclipse Ditto Digital Twin

Eclipse Ditto maintains a virtual representation (digital twin) of each water tank.

### Twin Structure

Each tank has a Thing with this structure:

```json
{
  "thingId": "water:TANK001",
  "policyId": "water:tank-policy",
  "attributes": {
    "tankId": "TANK001",
    "description": "Smart Water Tank TANK001",
    "location": "Plant Floor"
  },
  "features": {
    "waterQuality": {
      "properties": {
        "pH": 7.2,
        "turbidity": 2.5,
        "temperature": 28,
        "waterLevel": 80,
        "status": "SAFE",
        "alerts": [],
        "timestamp": "2024-01-15T10:30:00.000Z"
      }
    }
  }
}
```

### API Endpoints

```powershell
# Get all things
curl http://localhost:8085/api/2/things

# Get specific tank
curl http://localhost:8085/api/2/things/water:TANK001

# Get water quality properties only
curl http://localhost:8085/api/2/things/water:TANK001/features/waterQuality/properties

# Get just the status
curl http://localhost:8085/api/2/things/water:TANK001/features/waterQuality/properties/status
```

---

## 🧪 Testing Guide

### 1. Check All Containers Running

```powershell
docker compose ps
```

All containers should show "running" or "healthy".

### 2. Test MQTT Connection

```powershell
# Subscribe to all sensor data (in one terminal)
docker exec mosquitto mosquitto_sub -t "water/tank/+/sensors" -v

# Subscribe to alerts (in another terminal)
docker exec mosquitto mosquitto_sub -t "water/alerts" -v
```

### 3. Test Sensor Simulator

```powershell
# View simulator output
docker compose logs -f simulator
```

You should see JSON data being published every 5 seconds.

### 4. Test Node-RED Processing

Open http://localhost:1880 and check the debug sidebar (🐛 icon). You should see:
- Processed data with status classifications
- InfluxDB write responses (status code 204)
- Ditto update responses

### 5. Test InfluxDB Storage

```powershell
# Query via curl
curl -G "http://localhost:8086/api/v2/query?org=WaterMonitoring" ^
  -H "Authorization: Token my-super-secret-token-12345" ^
  -H "Accept: application/csv" ^
  -H "Content-Type: application/vnd.flux" ^
  --data-urlencode "q=from(bucket: \"water_quality\") |> range(start: -5m) |> limit(n: 5)"
```

Or open the InfluxDB UI at http://localhost:8086 and use the Data Explorer.

### 6. Test Grafana Dashboard

Open http://localhost:3000 → Dashboards → Smart Water Quality Monitoring.

You should see real-time values and graphs updating.

### 7. Test Ditto Digital Twin

```powershell
# Get TANK001 twin
curl http://localhost:8085/api/2/things/water:TANK001

# Get all twins
curl http://localhost:8085/api/2/things

# Get just the water quality properties
curl http://localhost:8085/api/2/things/water:TANK001/features/waterQuality/properties
```

### 8. Test Alert Generation

```powershell
# Subscribe to alerts
docker exec mosquitto mosquitto_sub -t "water/alerts" -v
```

Wait for the simulator to inject an abnormal value (every ~30 seconds).

### 9. Manual Alert Test

Publish a test message with abnormal values:

```powershell
docker exec mosquitto mosquitto_pub -t "water/tank/TANK001/sensors" -m '{"tankId":"TANK001","pH":3.0,"turbidity":15.0,"temperature":45.0,"waterLevel":5.0,"timestamp":"2024-01-15T10:30:00.000Z"}'
```

This should trigger an UNSAFE classification and generate alerts.

---

## 📊 Expected Output

### Simulator Terminal

```
============================================================
  Smart Water Quality Monitoring - Sensor Simulator
============================================================
  MQTT Broker : mosquitto:1883
  Interval    : 5 seconds
  Tanks       : TANK001, TANK002, TANK003
============================================================

[2024-01-15 10:30:00] Published to water/tank/TANK001/sensors: {"tankId":"TANK001","pH":7.12,...}
[2024-01-15 10:30:00] Published to water/tank/TANK002/sensors: {"tankId":"TANK002","pH":7.38,...}
[2024-01-15 10:30:00] Published to water/tank/TANK003/sensors: {"tankId":"TANK003","pH":6.92,...}

[ABNORMAL] Injecting 'high_turbidity' into TANK002
[2024-01-15 10:30:30] Published to water/tank/TANK002/sensors [ABNORMAL]: {"tankId":"TANK002","turbidity":15.3,...}
```

### Node-RED Debug Output

```json
{"tankId":"TANK001","pH":7.12,"turbidity":1.8,"temperature":27.5,"waterLevel":76.2,"status":"SAFE","alerts":[]}
{"tankId":"TANK002","pH":7.38,"turbidity":15.3,"temperature":25.1,"waterLevel":84.7,"status":"UNSAFE","alerts":["CRITICAL: Very high turbidity: 15.3 NTU"]}
```

---

## 🔧 Troubleshooting

### Container won't start

```powershell
# Check logs for errors
docker compose logs <service-name>

# Restart the service
docker compose restart <service-name>
```

### Node-RED can't connect to MQTT

- Ensure mosquitto is running: `docker compose ps mosquitto`
- Check mosquitto logs: `docker compose logs mosquitto`
- Verify the broker hostname is `mosquitto` (not `localhost`) in the Node-RED MQTT config

### InfluxDB not receiving data

- Check Node-RED debug sidebar for InfluxDB HTTP response codes
- Status 204 = successful write
- Status 401 = check token in .env file
- Status 404 = check org/bucket names

### Grafana shows "No data"

- Verify InfluxDB datasource is configured correctly in Grafana → Settings → Data Sources
- Check that data is being written to InfluxDB (use InfluxDB Data Explorer at http://localhost:8086)
- Make sure the time range is set to "Last 1 hour" or shorter

### Ditto returns 404

- Ensure the setup script has been run: `.\ditto\setup-ditto.ps1`
- Check Ditto gateway logs: `docker compose logs ditto-gateway`
- Wait longer for Ditto to fully initialize (Java services can take 60-90 seconds)

### Port conflicts

If a port is already in use, change it in docker-compose.yml:
```yaml
ports:
  - "NEW_PORT:ORIGINAL_PORT"
```

### Reset everything

```powershell
docker compose down -v
docker compose up -d
# Wait, then re-run setup script
```

---

## 🚀 Future Enhancements

1. **Email/SMS Alerts**: Integrate with notification services for real-time alerts
2. **Machine Learning**: Add anomaly detection using ML models in Node-RED
3. **More Sensors**: Add dissolved oxygen, chlorine, conductivity sensors
4. **Mobile Dashboard**: Create a mobile-friendly Grafana dashboard
5. **Predictive Maintenance**: Use historical data to predict tank maintenance needs
6. **Multi-Location**: Scale to monitor tanks across multiple locations
7. **Authentication**: Add proper MQTT authentication and Ditto user management
8. **Data Retention**: Configure InfluxDB retention policies for long-term storage
9. **Webhook Integration**: Send alerts to Slack, Teams, or Discord
10. **Historical Reports**: Generate automated PDF reports from Grafana

---

## 📄 Complete Workflow Summary

```
1. Sensor Simulator generates data for TANK001/002/003 every 5 seconds
2. Data published to Mosquitto via MQTT (water/tank/{tankId}/sensors)
3. Node-RED subscribes and receives the data
4. Node-RED VALIDATES the data (checks fields and ranges)
5. Node-RED applies THRESHOLD analysis (pH, turbidity, temp, water level)
6. Node-RED CLASSIFIES status: SAFE / WARNING / UNSAFE
7. Node-RED forwards processed data to:
   a. InfluxDB (for historical storage)
   b. Eclipse Ditto (to update digital twin)
   c. MQTT alerts topic (if WARNING or UNSAFE)
8. Grafana queries InfluxDB and displays real-time dashboards
9. Ditto maintains the latest state of each tank as a digital twin
```

---

**Built with ❤️ for IoT and Edge Computing education**
