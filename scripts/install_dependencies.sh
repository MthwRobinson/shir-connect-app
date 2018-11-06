# Enable the Postgres repository
sudo apt-get install wget ca-certificates
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'

# Install Postgres
sudo apt-get update
sudo apt-get install postgresql postgres-contrib

# Install Python 3 virtual environments
sudo apt-get install python-pip
pip install virtualenv
sudo apt-get install python3-venv
