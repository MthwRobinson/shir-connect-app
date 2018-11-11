#!/bin/bash

# Start the Flask server
cd /home/ubuntu/trs-dashboard/server/trs_dashboard/services
gunicorn -b 0.0.0.0:5000 app:app

# Start the node server
cd /home/ubuntu/trs-dashboard/server/trs_dashboard/ui
PORT=3001 serve -s build
