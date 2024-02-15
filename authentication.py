import requests
import base64
import configparser
import constants as c


class Authentication:
    def __init__(self) -> None:
        self.header = self.create_headers()
        self.access_token = ''
        self.expires_in = 0

    def create_headers(self):
        # Read client ID and secret from config file and store them in variables
        config = configparser.ConfigParser()
        config.read('secret.cfg')

        client_id = config.get('auth', 'client_id')
        client_secret = config.get('auth', 'client_secret')

        # Encode the client ID and secret as base64
        b64creds = base64.b64encode(
            f'{client_id}:{client_secret}'.encode()).decode('utf-8')

        # Set the request headers with the 'Authorization' token and Content-Type
        headers = {
            'Authorization': f'Basic {b64creds}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        return headers

    def refresh_access_token(self):

        # Send a POST request to the API endpoint with the headers and parameters
        response = requests.post(
            c.URL, headers=self.header, data=c.PARAMS, timeout=(3, 5))

        # If the response is successful, update the access token and expiration time
        if response.status_code == 200:
            response_data = response.json()
            self.access_token = response_data['access_token']
            self.expires_in = response_data.get('expires_in', 0)
        else:
            print('Error:', response.status_code, response.content)
