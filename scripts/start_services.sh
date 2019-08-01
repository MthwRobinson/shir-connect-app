# Start the airflow services
source $HOME/venv/etl/bin/activate
pm2 start "airflow scheduler" --name airflow_scheduler
pm2 start "airflow webserver -p 4999 airflow_server" --name airflow_server

# Dev Server
source $HOME/venv/dev/bin/activate
cd $HOME/dev/shir_connect/server/shir_connect/services
pm2 start "gunicorn -b 0.0.0.0:5000 app:app" --name dev_rest
cd $HOME/dev/shir_connect/ui
PORT=3000 pm2 start "serve -s build" --name  dev_ui

# Test Server
source $HOME/venv/test/bin/activate
cd $HOME/test/shir_connect/server/shir_connect/services
pm2 start "gunicorn -b 0.0.0.0:5001 app:app" --name test_rest
cd $HOME/test/shir_connect/ui
PORT=3001 pm2 start "serve -s build" --name  test_ui

# TRS Server
source $HOME/venv/trs/bin/activate
cd $HOME/trs/shir_connect/server/shir_connect/services
pm2 start "gunicorn -b 0.0.0.0:5002 app:app" --name trs_rest
cd $HOME/trs/shir_connect/ui
PORT=3002 pm2 start "serve -s build" --name  trs_ui
