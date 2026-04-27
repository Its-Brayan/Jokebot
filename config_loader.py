import yaml
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def load_write_config(config_path):
    path = os.path.join(BASE_DIR,'config',config_path)
    with open(path,'r') as f:
        config = yaml.safe_load(f)
        return config
def load_config(config_path):
    path = os.path.join(BASE_DIR,'config',config_path)
    with open(path,'r') as f:
        config = yaml.safe_load(f)
        return config