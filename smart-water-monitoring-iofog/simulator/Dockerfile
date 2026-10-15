# Python Sensor Simulator for Smart Water Quality Monitoring
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy simulator code
COPY sensor_simulator.py .

# Run with unbuffered output for real-time logging
CMD ["python", "-u", "sensor_simulator.py"]
