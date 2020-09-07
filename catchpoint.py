from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import os, requests, json, sys

class Catchpoint:
    def __init__(self, host='https://io.catchpoint.com/', api_url='ui/api/v1/'):
        self.host = host
        self.api_url = api_url
        # self._token = False
        self._token = 'scUoDLD/SZbahkAmHw9LtswNQqZ+kau6Ygc2qVX4Gnj92idpW4W0id7n8VU9u+aUUNqQ+sUGdGsY9uxBkVMMqqIvp+ahCW1ZNajVXAjYBsdRv7xLSuiskcjk0lA1/Cm+ov4wNT7Mkajr7aDOt1TbNgwcdQuzAyeYewOFRNU37wvzN76dgxoVNug2B2rwvoPGXGy6V/mXYWdAWgeaJDnxKGVQs7vgDI+zCHccdu/weM4kP2Jy'
        self._auth = False
        self.verbose = False
        self.content_type = "application/json"

    def _debug(self, msg):
        if self.verbose:
            sys.stderr.write(f"{msg}\n")
    
    def _authorize(self):
        url = f"{self.host}ui/api/token"
        config = {
            'client_id':os.environ.get('ID'),
            'client_secret':os.environ.get('SECRET')
        }
        
        self._debug("Creating auth url...")
        client = BackendApplicationClient(client_id=config['client_id'])
        catchpoint = OAuth2Session(client=client)
        data = catchpoint.fetch_token(token_url=url, client_id=config['client_id'], client_secret=config['client_secret'])

        self._token = data['access_token']
        print(data['access_token'])
    
    def _make_requests(self, url, method='GET', params=None, data=None):
        self._debug("Making request...")
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}
        try:
            r = requests.get(url, headers=headers)
            print(r.json())
        except KeyError as err:
            print(f"KeyError: {err}")
    
class Get(Catchpoint):
    def assertions(self):
        # if not self._auth:
        #     self._authorize()
        
        url = f"{self.host}{self.api_url}assertions"
        return self._make_requests(url)

    def nodes(self):
        # if not self._auth:
        #     self._authorize()

        url = f"{self.host}{self.api_url}nodes"
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}

        self._debug("Making request...")
        r = requests.get(url, headers=headers)
        nodes = r.json()['items']
        node_id = []
        for node in nodes:
            try:
                if node['network_type']['name'] == 'Enterprise': # Enterprise, Backbone, Lastmile...
                    print(node['id'], node['name'], node['city']['name'])
            except KeyError as err:
                print(err)
    
    # def product(self):

        
        
# cp = Get()
# print(cp.assertions())