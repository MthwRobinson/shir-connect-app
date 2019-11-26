""" Utility functions """
import os

import yaml

def get_config(project_path, config_file):
    """Pulls the configuration file based on the name of the
    folder where the project is located (since this is how
    name spaces are set up on the prod server). If there is no match,
    the default configuration is used."""
    config_path = os.path.join(project_path, 'configs')
    config_file = '{}.yml'.format(config_file)

    filename = os.path.join(config_path, config_file)
    with open(filename, 'r') as f:
        config = yaml.safe_load(f)
    return config
