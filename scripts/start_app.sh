#!/bin/bash

# Start the Flask server
cd /home/ubuntu/shir-connect/server/shir_connect/services
gunicorn -b 0.0.0.0:5000 app:app

# Start the node server
cd /home/ubuntu/shir-connect/server/shir_connect/ui
PORT=3001 serve -s build
