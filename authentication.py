import requests
import base64
import configparser
import constants as c

def get_access_token():

    # Read client ID and secret from config file and store them in variables
    config = configparser.ConfigParser()
    config.read('secret.cfg')

    client_id = config.get('auth', 'client_id')
    client_secret = config.get('auth', 'client_secret')

    # Encode the client ID and secret as base64
    b64creds = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode('utf-8')

    # Set the request headers with the 'Authorization' token and Content-Type
    headers = {
        'Authorization': f'Basic {b64creds}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Send a POST request to the API endpoint with the headers and parameters
    response = requests.post(c.URL, headers=headers, data=c.PARAMS)

    # If the response is successful, get the access token from the response content
    if response.status_code == 200:
        access_token = response.json()
        return access_token
    else:
        print('Error:', response.status_code, response.content)