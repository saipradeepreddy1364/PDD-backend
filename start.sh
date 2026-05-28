#!/bin/bash

echo "Starting Flask ML API on port 5000..."
cd /app/ml
python3 flask_api.py &

echo "Waiting for Flask to be ready..."
sleep 5

echo "Starting Spring Boot on port 8080..."
cd /app
java -jar app.jar