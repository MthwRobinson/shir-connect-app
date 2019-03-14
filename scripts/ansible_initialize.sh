ansible $1 --become -m raw -a "apt-get install -y python2.7"
ansible $1 --become -m raw -a "ln -s /usr/bin/python2.7 /usr/bin/python"
