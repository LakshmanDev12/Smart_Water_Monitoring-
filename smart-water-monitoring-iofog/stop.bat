@echo off
TITLE Stop Smart Water Quality Monitoring
echo Stopping all Docker containers...
docker compose down
echo.
echo All services stopped cleanly.
timeout /t 3
