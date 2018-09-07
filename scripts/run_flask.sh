#!/bin/bash
cd ../server/trs_dashboard/services
gunicorn -b 0.0.0.0:5000 app:app
