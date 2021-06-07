
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

app.config['CORS_HEADERS'] = 'Content-Type'

# Routes for different functionalities of the application
@app.route('/generate', methods=['POST'])
# Generate endpoint uses OpenAI API to generate text based on a given prompt and temperature
def generate():
    data = request.get_json()
    prompt = data.get('prompt')
    temperature = data.get('temperature', 0.5)
    generated_text = client.ChatCompletion.create(engine="gpt-4-1106-preview", 
    prompt=prompt, 
    temperature=temperature,
    max_tokens=28000, #default max is 4096 for text-davinci-003, errors with sentiment analysis were caused by gpt-4-32k-0613 here when Chat was missing from ChatCompletion (changing to 3700 as errors were occurring where the prompt was consuming more tokens in addition to completion causing total to go above max).
    n=2,
    stop=None,
    log_level="info"                                          
                                              
    )
    return jsonify({'generated_text': generated_text})

@app.route('/complete', methods=['POST'])
# Complete endpoint uses OpenAI API to complete given text 
def complete():
    data = request.get_json()
    text = data.get('text')
    completed_text = client.ChatCompletion.create(model="gpt-4-1106-preview",
    text=text,
    max_tokens=28000 #default max is 4096 for text-davinci-003, errors with sentiment analysis were caused by gpt-4-32k-0613 here when Chat was missing from ChatCompletion (changing to 3700 as errors were occurring where the prompt was consuming more tokens in addition to completion causing total to go above max).
    )
    return jsonify({'completed_text': completed_text})

@app.route('/search', methods=['POST'])
# Search endpoint uses OpenAI API to search based on a given query
def search():
    data = request.get_json()
    query = data.get('query')
    response = client.Completion.create(
        engine="gpt-4-1106-preview", # upgraded from gpt-4-32k-0314 which supports 128k tokens, default is gpt-3.5-turbo-0301 
        prompt=query,
        max_tokens=120000
    )
    generated_text = response.choices[0].text.strip()
    return jsonify({'results': generated_text})

@app.route('/playground', methods=['POST'])
# Playground endpoint uses OpenAI API to generate code based on a given prompt
def playground():
    data = request.get_json()
    code = data.get('code')
    response = client.Completion.create(
        engine="gpt-4-1106-preview", # upgraded to gpt-4-1106-preview from gpt-4-32k-0314, default is gpt-3.5-turbo-0301 
        prompt=code,
        max_tokens=120000
    )
    generated_text = response.choices[0].text.strip()
    return jsonify({'output': generated_text})

@app.route('/logo.png')
# Serves logo image
def serve_logo():
    return send_from_directory('.', 'logo.png', mimetype='image/png')

@app.route('/openapi.yaml')
# Serves OpenAPI specification
def serve_openai_yaml():
    return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')

@app.route('/.well-known/ai-plugin.json')
# Serves AI plugin manifest
def serve_ai_plugin_manifest():
    return send_from_directory('.well-known', 'ai-plugin.json', mimetype='application/json')

@app.route('/prices', methods=['GET', 'POST'])
# Prices endpoint fetches forex price data from OANDA API
def get_prices():
    if request.method == 'POST':
        data = request.get_json()
    else:  # It's a GET request
        data = request.args.to_dict()

    if not data or not all(key in data for key in ['instrument', 'from_time', 'granularity', 'price']):
        prompt = "Please provide the following details for the price data:\n"
        prompt += "1. Instrument (currency pair): For example, 'EUR_USD'\n"
        prompt += "2. From time (start time for the analysis): For example, '2022-1-17T15:00:00.000000000Z'\n"
        prompt += "3. Granularity (time interval for the analysis): For example, 'H1' (hourly), 'D' (daily), 'M' (monthly), etc."
        prompt += "4. Price: 'A' for Ask, 'B' for Bid, 'M' for Midpoint"
        return jsonify({'message': prompt}), 400

    instrument = data.get('instrument')
    from_time = data.get('from_time')
    granularity = data.get('granularity')
    price = data.get('price')

    oanda_api_key = os.getenv("OANDA_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    plugin = OpenAIPlugin(oanda_api_key, openai_api_key)

    candles = plugin.get_oanda_candles(instrument, from_time, granularity, price)