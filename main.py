
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