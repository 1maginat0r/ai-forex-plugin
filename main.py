
# Import necessary modules and libraries
import os
from openai import OpenAI
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
from flask import make_response
import numpy as np
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
import yaml


# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load YAML file (removing in production)
#with open('openapi.yaml', 'r') as yaml_file:
  # yaml_data = yaml.safe_load(yaml_file)
   
token = os.getenv('OANDA_TOKEN')
accounts = [os.getenv('ACCOUNT1'), os.getenv('ACCOUNT2')]
active_account = os.getenv('ACTIVE_ACCOUNT')
username = os.getenv('OANDA_USERNAME')

# Set values from environment variables (removing in production)
#yaml_data['oanda']['token'] = os.getenv('OANDA_TOKEN')
#yaml_data['oanda']['accounts'] = [os.getenv('ACCOUNT1'), os.getenv('ACCOUNT2')]
#yaml_data['oanda']['active_account'] = os.getenv('ACTIVE_ACCOUNT')
#yaml_data['oanda']['username'] = os.getenv('OANDA_USERNAME')

# Save modified YAML file (removing in production)
#with open('openapi.yaml', 'w') as yaml_file:
 # yaml.dump(yaml_data, yaml_file)

# Setup Flask app
app = Flask(__name__)

# Enable CORS and configure CORS Headers
cors = CORS(app, resources={
    r"/*": {
        "origins": "https://chat.openai.com",  # Update this to the origin you want to allow
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Credentials",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Origin",
            "Baggage",
            "sentry-trace",
            "openai-conversation-id",
            "openai-ephemeral-user-id"  
        ]
    }
})