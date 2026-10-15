# Eclipse ioFog Edge Processing Microservice
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY iofog_edge_processor.py .

CMD ["python", "-u", "iofog_edge_processor.py"]
