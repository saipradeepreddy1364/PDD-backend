#!/bin/bash

echo "Starting Flask ML API on port 5000 (gunicorn)..."
cd /app/ml
# gunicorn: production WSGI server, bound to localhost only so Render
# routes all public traffic to Spring Boot (port 8080/10000), not Flask.
gunicorn --bind 127.0.0.1:5000 --workers 1 --timeout 120 flask_api:app &

echo "Waiting for Flask to be ready..."
sleep 5

echo "Starting Spring Boot on port 8080..."
cd /app
java -jar app.jar