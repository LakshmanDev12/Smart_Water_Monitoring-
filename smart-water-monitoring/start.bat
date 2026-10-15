@echo off
TITLE Start Smart Water Quality Monitoring
echo Starting Docker containers...
docker compose up -d
echo.
echo All services started successfully!
echo.
echo Grafana Dashboard : http://localhost:3000/d/water-quality-dashboard
echo Node-RED Flow     : http://localhost:1880
echo InfluxDB UI       : http://localhost:8086
echo Eclipse Ditto API : http://localhost:8085/api/2/things
echo.
echo Opening Grafana Dashboard...
start http://localhost:3000/d/water-quality-dashboard
timeout /t 5
