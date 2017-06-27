# fitbit.py

# to open source envs/base/bin/activate

import json
import os
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from functools import partial
from urllib.parse import urlparse, parse_qs
import requests
import fitbit_config


def main(dt, detail):

    # start server for auth responses
    thread = threading.Thread(target = partial(run, port=1410))
    thread.daemon = True
    thread.start()
    time.sleep(1)

    fitbit_auth = FitBitAuthHandler()

    headers = {'Authorization': 'Bearer {token}'.format(token=fitbit_auth.access_token_dict['access_token'])}
    user_id = fitbit_auth.user_id

    # prepare output dir
    if not os.path.isdir(fitbit_config.output_dir):
        os.mkdir(fitbit_config.output_dir)
    for extract in fitbit_config.extracts:
        print('making request for:\n' + str(extract))
        if dt:
            extract['params']['date'] = dt
            extract['params']['end-date'] = dt
        if detail:
            extract['params']['detail-level'] = detail
        r = requests.get(extract['url'].format(**extract['params']), headers=headers)
        print(r.status_code)
        data_file = os.path.join(fitbit_config.output_dir, extract['output_file'])
        with open(data_file, 'w+') as f:
            json.dump(r.json(), f)
            print('successfully wrote: ' + f.name)

        # flatten time series
        with open(data_file, 'r') as f:
            json_data = json.load(f)
        flattened = extract['flatten_func'](json_data)
        with open(os.path.join(fitbit_config.output_dir, extract['flattened_file']), 'w') as f:
            for row in flattened:
                f.write(','.join(str(e) for e in row) + '\n')
            print('successfully wrote: ' + f.name)


class FitBitAuthHandler():

    def __init__(self):
        self.client_id = fitbit_config.client_id
        self.client_secret = fitbit_config.client_secret
        self.oauth_uri = fitbit_config.oauth_uri
        self.token_uri = fitbit_config.token_uri
        self.scope = fitbit_config.scope
        self.redirect_uri = fitbit_config.callback_url
        self.expires_in = 2592000
        self.response_type = 'code'
        self.auth_params = {'response_type': self.response_type,
                        'client_id': str(self.client_id),
                        'scope': self.scope,
                        'redirect_uri': self.redirect_uri}

        if os.path.isfile('access_token.json'):
            with open('access_token.json', 'r') as f:
                self.access_token_dict = json.load(f)
        else:
            auth_code = self._get_auth_code()
            self.access_token_dict = self._get_access_token(auth_code)
        self.basic_auth = requests.auth.HTTPBasicAuth('Bearer', self.access_token_dict['access_token'])
        self.user_id = self.access_token_dict['user_id']

    def _get_auth_code(self):
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        r = requests.post(self.oauth_uri, auth=auth, params=self.auth_params)
        print(r.status_code)
        with open(fitbit_config.html_loc, 'w') as f:
            f.write(r.text)
        if os.path.isfile('auth_code.txt'):
            os.remove('auth_code.txt')
        webbrowser.open_new(fitbit_config.html_loc)
        while not os.path.isfile('auth_code.txt'):
            time.sleep(1)
        with open('auth_code.txt', 'r') as f:
            auth_code = f.read()
        return auth_code


    def _get_access_token(self, auth_code):
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        token_params = {'code': auth_code, 'grant_type': 'authorization_code',
                        'client_id': self.client_id, 'redirect_uri': self.redirect_uri}
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        r = requests.post(self.token_uri, auth=auth, headers=headers, params=token_params)
        if r.status_code == 200:
            with open('access_token.json', 'w') as f:
                json.dump(r.json(), f)
        return r.json()


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        print(parse_qs(urlparse(self.path).query))
        auth_code = parse_qs(urlparse(self.path).query)['code'][0]
        print(auth_code)
        with open('auth_code.txt', 'w') as f:
            f.write(auth_code)
            print('success')
        self._set_headers()
        self.wfile.write(b'<html><body><h1>auth_code</h1></body></html>')

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting http server...')
    httpd.serve_forever()


if __name__ == '__main__':
    try:
        dt = sys.argv[1]
    except IndexError:
        dt = None

    try:
        detail = sys.argv[2]
    except IndexError:
        detail = None

    print(dt, detail)
    main(dt, detail)
