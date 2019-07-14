###################################################################
# This scripts runs in the before_script step of the
# deployment stages in the .gitlab-ci.yml file.
# It installs all of the dependencies that are required
# to create the front end build and push out updates to the server.
####################################################################

# Install open ssh and add remote server to known hosts
apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*
apt-get update && sudo apt-get install -y openssh-server
mkdir -p $HOME/.ssh
echo "$SSH_PRIVATE" | tr -d '\r' > ~/.ssh/id_rsa
chmod 0600 $HOME/.ssh/id_rsa
echo $SSH_PUBLIC >> $HOME/.ssh/id_rsa.pub
chmod 0600 $HOME/.ssh/id_rsa.pub
ssh-agent bash -s
ssh-keyscan -H 3.221.129.51 >> $HOME/.ssh/known_hosts

# Install NVM and NPM
sudo apt-get update && sudo apt-get -y install curl
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.0/install.sh | bash

# Install Ansible
sudo apt-get update
sudo apt-get -y install software-properties-common
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get -y install ansible
echo "[shir_connect]" >> $HOME/hosts
echo "ubuntu@3.221.129.51" >> $HOME/hosts
