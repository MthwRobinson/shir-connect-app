#!/bin/bash
cd ../server/shir_connect/services
gunicorn -b 0.0.0.0:5000 app:app
