#!/bin/sh
LOCK=/var/tmp/eventbrite_load
if [ -f $LOCK ]; then
  echo Eventbrite load is already running\!
  exit 6
fi
touch $LOCK
echo Eventbrite load is starting
. $HOME/set_environment.sh
/home/ubuntu/venv/trs_dashboard/bin/trs_dashboard load_eventbrite
rm $LOCK
