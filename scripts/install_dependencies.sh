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

# Install NVM and Node
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.0/install.sh | bash
nvm install node
nvm install --lts
nvm use --lts

# Install global npm packages
npm install -g serve
npm install -g pm2

# Nginx
sudo wget http://nginx.org/keys/nginx_signing.key
sudo apt-key add nginx_signing.key
sudo apt-get update
sudo apt-get install nginx

# Let's Encrypt
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx
