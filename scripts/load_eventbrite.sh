#!/bin/sh
LOCK=/var/tmp/eventbrite_load
if [ -f $LOCK ]; then
  echo Eventbrite load is already running\!
  exit 6
fi
touch $LOCK
echo Eventbrite load is starting
$HOME/venv/shir_connect/bin/shir_connect load_eventbrite
$HOME/venv/shir_connect/bin/shir_connect update_geometries
$HOME/venv/shir_connect/bin/shir_connect match_participants
$HOME/venv/shir_connect/bin/shir_connect refresh_views
rm $LOCK
