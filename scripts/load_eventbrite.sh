#!/bin/sh
LOCK=/var/tmp/eventbrite_load
if [ -f $LOCK ]; then
  echo Eventbrite load is already running\!
  exit 6
fi
touch $LOCK
echo Eventbrite load is starting
/home/ubuntu/venv/shir_connect/bin/shir_connect load_eventbrite
/home/ubuntu/venv/shir_connect/bin/shir_connect update_geometries
/home/ubuntu/venv/shir_connect/bin/shir_connect match_participants
/home/ubuntu/venv/shir_connect/bin/shir_connect refresh_views
rm $LOCK
