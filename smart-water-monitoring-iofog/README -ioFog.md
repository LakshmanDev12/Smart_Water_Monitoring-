# 🌊 Smart Water Quality Monitoring — Eclipse ioFog Edition

A complete IoT-based smart water tank monitoring system and Digital Twin powered by **Eclipse ioFog Edge Architecture**.

---

## 📊 Comparison: Project 1 vs. Project 2

| Feature | Project 1 (`smart-water-monitoring`) | Project 2 (`smart-water-monitoring-iofog`) |
|---|---|---|
| **Folder Path** | `E:\Cloud\smart-water-monitoring` | `E:\Cloud\smart-water-monitoring-iofog` |
| **Edge Computing Layer** | **Node-RED** Flow Engine (Port 1880) | **Eclipse ioFog Edge Processor** Microservice |
| **Edge Microservice** | Node-RED JavaScript rules flow | Dedicated ioFog Edge Container (`iofog-edge-processor`) |
| **Telemetry Transport** | Eclipse Mosquitto MQTT (Port 1883) | Eclipse Mosquitto MQTT (Port 1883) |
| **Time-Series DB** | InfluxDB 2.x (Port 8086) | InfluxDB 2.x (Port 8086) |
| **Visualization** | Grafana Dashboard (Port 3000) | Grafana Dashboard (Port 3000) |
| **Digital Twin** | Eclipse Ditto (Port 8085) | Eclipse Ditto (Port 8085) |

---

## 🏗️ System Architecture (Eclipse ioFog Edition)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ECLIPSE IOFOG PLATFORM                              │
│                    (Edge Compute Network Orchestration)                     │
│                                                                             │
│   ┌───────────────────────────┐         ┌───────────────────────────────┐   │
│   │   ioFog Controller        │ ──────► │   ioFog Agent (Edge Node)     │   │
│   │   (Central Management)    │         │   (Runs Microservices)        │   │
│   └───────────────────────────┘         └──────────────┬────────────────┘   │
└────────────────────────────────────────────────────────┼────────────────────┘
                                                         │ Manages Containers
                                                         ▼
                                          ┌───────────────────────────────┐
                                          │  1. Sensor Simulator (Python) │
                                          │  2. MQTT Broker (Mosquitto)   │
                                          │  3. ioFog Edge Processor      │
                                          └──────────────┬────────────────┘
                                                         │ Filtered / Classified Data
                                           ┌─────────────┴─────────────┐
                                           ▼                           ▼
                                ┌────────────────────┐      ┌────────────────────┐
                                │ InfluxDB + Grafana │      │   Eclipse Ditto    │
                                │ (Time-Series & UI) │      │   (Digital Twin)   │
                                └────────────────────┘      └────────────────────┘
```

---

## 🚀 How to Run Project 2 (ioFog Edition)

### Method 1: 1-Click Launch (Recommended)
Open `E:\Cloud\smart-water-monitoring-iofog` and double-click:
👉 **`setup.bat`** *(or `start.bat`)*

### Method 2: ioFog ECN Deployer (via WSL2)
Double-click:
👉 **`run_iofog_wsl.bat`**

---

## 🌐 Web Endpoints & Dashboards

- **📊 Grafana Dashboard**: [http://localhost:3000/d/water-quality-dashboard](http://localhost:3000/d/water-quality-dashboard) `(admin / admin)`
- **🛢️ InfluxDB UI**: [http://localhost:8086](http://localhost:8086) `(admin / adminpassword123)`
- **🌐 Eclipse Ditto Digital Twin**: [http://localhost:8085/api/2/things](http://localhost:8085/api/2/things)
- **📡 Mosquitto Broker**: `localhost:1883`
