# Smart Water Monitoring and Digital Twin

A Docker-based IoT project for monitoring water quality, detecting abnormal conditions, generating alerts, visualizing historical data, and maintaining a digital twin of each water tank.

## Overview

The **Smart Water Monitoring and Digital Twin** project combines IoT messaging, edge processing, time-series data storage, visualization, and digital twin technology to monitor water tank conditions.

The system accepts water-quality measurements, validates sensor data, evaluates threshold conditions, classifies the water status, and presents the results through dashboards and alerts.

This repository contains two implementations:

1. **Smart Water Monitoring** — A Docker-based implementation using MQTT, Node-RED, InfluxDB, Grafana, and Eclipse Ditto.
2. **Smart Water Monitoring with Eclipse ioFog** — An edge-computing implementation using a Python edge processor and Eclipse ioFog.

## Objectives

- Monitor water quality and tank conditions.
- Validate incoming sensor data.
- Detect abnormal water-quality measurements.
- Classify water conditions as SAFE, WARNING, or UNSAFE.
- Generate alerts when abnormal conditions are detected.
- Store historical measurements for analysis.
- Visualize water-quality trends and tank status.
- Represent each water tank as a digital twin.
- Explore edge processing using Eclipse ioFog.
- Deploy and manage services using Docker containers.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Sensor simulation and edge-processing logic |
| Docker | Containerized deployment |
| Docker Compose | Multi-service orchestration |
| Eclipse Mosquitto | MQTT message broker |
| Node-RED | Data processing and workflow automation |
| InfluxDB | Time-series data storage |
| Grafana | Dashboards and historical visualization |
| Eclipse Ditto | Digital twin management |
| Eclipse ioFog | Edge-computing deployment and management |
| cURL / Postman | API testing and verification |

## System Architecture

### Implementation 1: Docker-Based Monitoring

```text
Sensor Simulator
       |
       v
 MQTT Publisher
       |
       v
Eclipse Mosquitto
       |
       v
    Node-RED
       |
       v
Data Validation
       |
       v
Threshold Checking
       |
       v
Status Classification
       |
       +------------------+
       |                  |
       v                  v
    InfluxDB          MQTT Alerts
       |
       v
    Grafana

Sensor / Processing State
       |
       v
  Eclipse Ditto
       |
       v
  Digital Twin API
```

### Implementation 2: Eclipse ioFog Edge Processing

```text
Sensor Simulator
       |
       v
   MQTT Broker
       |
       v
 Eclipse ioFog
       |
       v
Python Edge Processor
       |
       +----------------------+
       |                      |
       v                      v
Validation and Analysis   Alert Generation
       |
       v
Status Classification
       |
       v
Monitoring and Data Output
```

The exact integrations and deployment steps depend on the configuration in each project folder.

## Water Quality Parameters

The system is designed to process the following measurements:

| Parameter | Description |
|---|---|
| Tank ID | Unique identifier for a water tank |
| pH Level | Indicates the acidity or alkalinity of water |
| Turbidity | Indicates water cloudiness caused by suspended particles |
| Temperature | Measures water temperature |
| Water Level | Indicates the amount of water in the tank |
| Timestamp | Records when the measurement was collected |

## Water Quality Classification

The processing layer evaluates measurements against configured thresholds.

| Status | Meaning |
|---|---|
| SAFE | Measurements are within the configured acceptable ranges |
| WARNING | A measurement approaches or crosses a configured warning threshold |
| UNSAFE | A measurement violates a configured critical threshold |

**Note:** The classification depends on the thresholds configured in the application. These software classifications do not independently certify water as safe for drinking.

## Role of Each Component

### 1. Sensor Simulator
Generates sample water-quality measurements for development and testing without requiring physical sensors.

### 2. Eclipse Mosquitto
Acts as the MQTT broker, receiving published sensor messages and distributing them to subscribed components.

### 3. Node-RED
Processes incoming messages, validates values, checks thresholds, classifies water conditions, and routes data to storage and alert workflows.

### 4. InfluxDB
Stores timestamped measurements so that water-quality changes can be analyzed over time.

### 5. Grafana
Displays water-quality readings, tank conditions, alerts, and historical trends using dashboards.

### 6. Eclipse Ditto
Maintains digital representations of water tanks and their reported state through digital twin APIs.

### 7. Eclipse ioFog
Supports deployment and management of edge applications. In the ioFog implementation, the Python edge processor performs local validation, threshold checking, classification, and alert generation according to its configured workflow.

## Project Structure

```text
Smart_Water_Monitoring/
│
├── smart-water-monitoring/
│   ├── Docker Compose configuration
│   ├── Node-RED flows
│   ├── Mosquitto configuration
│   ├── InfluxDB configuration
│   ├── Grafana dashboards
│   ├── Eclipse Ditto configuration
│   └── Supporting scripts and files
│
├── smart-water-monitoring-iofog/
│   ├── Python edge processor
│   ├── Eclipse ioFog deployment configuration
│   ├── Sensor simulation and messaging files
│   └── Supporting scripts and files
│
├── .gitignore
└── README.md
```

*The tree above describes the intended organization. Actual filenames and subfolders may differ depending on the files included in each implementation.*

## Prerequisites

Install the following tools before running the project:

- Docker Desktop
- Docker Compose
- Git
- Python, if running Python scripts directly
- A modern web browser
- cURL or Postman for API testing

For the ioFog implementation, follow the setup instructions provided in its project folder and verify the required agent and controller components are available.

## Getting Started

### Step 1: Clone the repository

```bash
git clone https://github.com/LakshmanDev12/Smart_Water_Monitoring-.git
cd Smart_Water_Monitoring-
```

### Step 2: Choose an implementation

For the Docker-based version:

```bash
cd smart-water-monitoring
```

For the Eclipse ioFog version:

```bash
cd ../smart-water-monitoring-iofog
```

### Step 3: Configure the environment

Review the configuration files and any setup instructions in the selected folder.

Configure required ports, service credentials, MQTT topics, database settings, digital twin identifiers, and threshold values as appropriate.

Do not commit `.env` files containing passwords, tokens, or other secrets. Provide a sanitized `.env.example` file when environment variables are required.

### Step 4: Start the Docker-based implementation

From the folder containing the relevant Compose file, run:

```bash
docker compose up -d
```

If the Compose file has a different name or is stored in another directory, specify its actual path using the `-f` option.

Check the container status:

```bash
docker compose ps
```

View service logs:

```bash
docker compose logs -f
```

### Step 5: Run the ioFog implementation

Navigate to `smart-water-monitoring-iofog` and follow the included deployment scripts and configuration.

Verify that the ioFog agent is connected to its controller, the Python edge processor is deployed, and the required messaging endpoints are reachable.

Use the project's configured commands and logs to verify deployment.

## Testing and Verification

Use the following checklist to validate the implementation:

- [ ] Docker containers start successfully.
- [ ] The sensor simulator publishes measurements.
- [ ] MQTT messages reach the processing workflow.
- [ ] Invalid sensor values are handled appropriately.
- [ ] SAFE, WARNING, and UNSAFE conditions are tested.
- [ ] Alerts are generated for configured abnormal conditions.
- [ ] Measurements are stored in InfluxDB.
- [ ] Grafana displays current and historical readings.
- [ ] Eclipse Ditto exposes the configured tank digital twin.
- [ ] The ioFog agent and Python processor operate successfully in the second implementation.

## Expected Outcomes

The completed system should demonstrate:

- Automated water-quality monitoring.
- Detection and classification of abnormal measurements.
- MQTT-based communication between components.
- Time-series storage and historical analysis.
- Dashboard-based visualization.
- Digital twin representation of water tanks.
- Containerized deployment.
- Edge-processing capabilities in the Eclipse ioFog implementation.

## Future Enhancements

- Integration with physical pH, turbidity, temperature, and water-level sensors.
- Real-time notifications through email or mobile applications.
- Improved anomaly detection using machine learning.
- Configurable thresholds for different tank types.
- Secure device authentication and encrypted communication.
- Remote monitoring of multiple water tanks.
- Automated maintenance and sensor-health monitoring.

## Documentation

- [Docker Documentation](https://docs.docker.com/)
- [Node-RED Documentation](https://nodered.org/docs/)
- [Eclipse Mosquitto](https://mosquitto.org/documentation/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Eclipse Ditto Documentation](https://eclipse.dev/ditto/)
- [Eclipse ioFog](https://iofog.org/)

## License

Choose and add an appropriate open-source license before distributing the project. Until a license is added, do not assume that others have permission to reuse or redistribute the source code.

## Author

**Smart Water Monitoring and Digital Twin Project**

Developed to demonstrate IoT monitoring, edge computing, data visualization, and digital twin technologies.
