# Runs the production build for the front end
echo "Running the production build for the UI ..."
cd $HOME/shir-connect/ui
npm run build

# Moves the build folder to the remote server
echo "Stopping all running processes ... "
ssh -i $HOME/certs/dataflock.pem ubuntu@13.58.50.14 \
    "/home/ubuntu/.nvm/versions/node/v11.0.0/bin/pm2 stop all"
echo "Deleting current build file ... "
ssh -i $HOME/certs/dataflock.pem ubuntu@13.58.50.14 \
    "rm -rf /home/ubuntu/shir-connect/ui/build"
echo "SCP the build file to the dev server ..."
scp -i $HOME/certs/dataflock.pem \
    -r $HOME/shir-connect/ui/build \
    ubuntu@13.58.50.14:/home/ubuntu/shir-connect/ui

# Pulls down the latest code from the master branch
echo "Pulling the latest code from git ... "
ssh -i $HOME/certs/dataflock.pem ubuntu@13.58.50.14 \
    "cd /home/ubuntu/shir-connect && git checkout master && git pull origin master"
echo "Migrating database tables ..."
ssh -i $HOME/certs/dataflock.pem ubuntu@13.58.50.14 \
    "cd /home/ubuntu/shir-connect/database/ && shmig -t postgresql -d postgres up"
echo "Refreshing materialized views ..."
ssh -i $HOME/certs/dataflock.pem ubuntu@13.58.50.14 \
      "/home/ubuntu/venv/shir_connect/bin/shir_connect initialize --drop_views"
echo "Installing new python dependencies ..."
ssh -i $HOME/certs/dataflock.pem ubuntu@13.58.50.14 \
    "cd /home/ubuntu/shir-connect/server/ && /home/ubuntu/venv/shir_connect/bin/pip install -e ."

# Restart service
echo "Restarting all process ..."
ssh -i $HOME/certs/dataflock.pem ubuntu@13.58.50.14 \
    "/home/ubuntu/.nvm/versions/node/v11.0.0/bin/pm2 start all"

echo "Done!"


