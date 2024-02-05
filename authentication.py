import requests
import base64
import configparser

def get_access_token():
    
    # Set the API endpoint URL and grant_type parameter
    url = 'https://auth.tidal.com/v1/oauth2/token'
    params = {'grant_type': 'client_credentials'}

    # Set the client ID and secret
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
    response = requests.post(url, headers=headers, data=params)

    # If the response is successful, get the access token from the response content
    if response.status_code == 200:
        access_token = response.json()['access_token']
        return access_token
    else:
        print('Error:', response.status_code, response.content)