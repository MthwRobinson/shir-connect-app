#!/usr/bin/sh
LOCK=/var/tmp/eventbrite_load
if [ -f $LOCK ]; then
  echo Eventbrite load is already running\!
  exit 6
fi
touch $LOCK
echo Eventbrite load is starting
source /home/trs_dashboard/.bashrc
/home/trs_dashboard/anaconda3/bin/trs_dashboard load_eventbrite
rm $LOCK
