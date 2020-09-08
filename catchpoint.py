from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import os, requests, json, sys, time



class Catchpoint:
    def __init__(self, host='https://io.catchpoint.com/', api_url='ui/api/v1/'):
        self.host = host
        self.api_url = api_url
        self._token = None
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
    def Assertions(self):
        # if not self._auth:
        #     self._authorize()
        
        url = f"{self.host}{self.api_url}assertions"
        return self._make_requests(url)

    def Nodes(self):
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
    
    def Products(self):
        # if not self._auth:
        #     self._authorize()

        url = f"{self.host}{self.api_url}products"
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}

        self._debug("Making request...")
        r = requests.get(url, headers=headers)
        products = r.json()['items']
        products_id = []
        with open('output/products.json', 'w', encoding='utf-8') as f:
            for product in products:                
                json.dump(product, f, ensure_ascii=False, indent=4)
                products_id.append(product['id'])
        return products_id
        
    def Folders(self):
        # if not self._auth:
        #     self._authorize()

        product_id = self.Products()
        folders_id = []

        for folders in product_id:
            try: 
                # time.sleep(1)
                url = f"{self.host}{self.api_url}folders?productId={folders}"
                headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}

                self._debug("Making request...")
                r = requests.get(url, headers=headers)
                folder = r.json()['items']

                for folder_id in folder:
                    with open('output/folders.json', 'a', encoding='utf-8') as f:
                        json.dump(folder_id, f, ensure_ascii=False, indent=4)
                        folders_id.append(folder_id['id'])
                        print(folder_id['id'])
                # print(folder)
            except ValueError:
                # print(f"{{\'id\'{folders}: \'no folder found\'}}")
                pass

    def Tests(self):
        pass




# cp = Get()
# print(cp.Assertions())