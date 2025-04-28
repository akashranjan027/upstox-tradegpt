import json
import webbrowser
from flask import Flask, request
import upstox_client
from upstox_client.api import LoginApi
import os
import time

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def get_upstox_client():
    config = load_config()
    if 'access_token' in config and config['access_token']:
        configuration = upstox_client.Configuration()
        configuration.access_token = config['access_token']
        return upstox_client.ApiClient(configuration)
    return None

def get_token():
    config = load_config()
    return config.get('access_token')

def refresh_token(refresh_token):
    pass

def start_authentication():
    pass 