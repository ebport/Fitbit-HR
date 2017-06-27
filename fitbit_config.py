'''
File for configuration and specifications of the fitbit data extracts
'''
import keys

# app configuration - must match https://dev.fitbit.com/apps
client_id = keys.client_id
client_secret = keys.client_secret
callback_url = 'http://localhost:1410/'
oauth_uri = 'http://www.fitbit.com/oauth2/authorize'
token_uri = 'https://api.fitbit.com/oauth2/token'
html_loc = keys.html_loc

# space delimited string of access https://dev.fitbit.com/docs/oauth2/#scope
scope = 'heartrate'

# filesystem info
output_dir = 'fitbit_data'

# flatten funcs
def flatten_hr_intraday(hr_json):
    day = hr_json['activities-heart'][0]['dateTime']
    records = hr_json['activities-heart-intraday']['dataset']
    flattened = [('day', 'time', 'hr')]
    for r in records:
        flattened.append((day, r['time'], r['value']))
    return flattened

# extracts
extracts = [{
'url': 'https://api.fitbit.com/1/user/-/activities/heart/date/{date}/{end-date}/{detail-level}.json',
'params': {
    'date': 'today',
    'end-date': 'today',
    'detail-level': '1min'},
'output_file': 'hr.json',
'flatten_func': flatten_hr_intraday,
'flattened_file': 'hr.csv'
}]
