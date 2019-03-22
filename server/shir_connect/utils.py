""" Utility functions """
import os

import requests
import yaml

def get_config(project_path, home_path):
    """ Pulls settings from the configs folder with the following
    order of precedence:
    1. If a config file lists the IP address of the server, us that config
    2. Otherwise, use the config that is marked as the default
    """
    custom_config = {}
    config_path = os.path.join(project_path, 'configs')
    config_files = os.listdir(config_path)
    ip_addr = get_ip(home_path)
    for file_ in config_files:
        filename = config_path + '/' + file_
        with open(filename, 'r') as f:
            config = yaml.safe_load(f)
        if ip_addr in config['ip_addresses']:
            custom_config = config
            break
        if config['default']:
            default_config = config
    if not custom_config:
        custom_config = default_config
    return custom_config

def get_ip(home_path):
    """ Determines the IP address of the server. """
    files = os.listdir(home_path)
    ip_file = '.shir-connect-ip'
    filename = os.path.join(home_path, ip_file)
    if ip_file in files:
        with open(filename, 'r') as f:
            ip_addr = f.readline()
    else:
        ip_addr = requests.get('https://api.ipify.org').text
        with open(filename, 'w') as f:
            f.write(ip_addr)
    return ip_addr
