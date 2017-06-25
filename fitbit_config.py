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

# extracts
extracts = [{
'url': 'https://api.fitbit.com/1/user/{user-id}/activities/heart/date/{date}/{period}.json',
'params': {
    'user-id': '-',
    'date': '2017-05-31',
    'period': '1d'},
'output_file': 'hr.json'
}]
# ,
# {
# 'url': 'https://api.fitbit.com/1.2/user/{user-id}/sleep/date/{startDate}/{endDate}.json',
# 'params': {
#     'user-id': '-',
#     'startDate': '2017-05-01',
#     'endDate': '2017-05-28'},
# 'output_file': 'sleep.json'
# }
# ]

# flattened extracts
# activities-heart-intraday: {"datasetInterval": 1, "datasetType": "minute",
# "dataset": [{"value": 61, "time": "00:24:00"}
# "activities-heart": [{"dateTime": "2017-05-31"
flatten_schema = [
    {'input_file': 'hr.json',
    'output_file': 'hr.csv',
    'output_schema': {'dt': ['activities-heart', 'dateTime'],
                      'time': ['activities-heart-intraday', 'dataset', 'time'],
                      'hr': ['activities-heart-intraday', 'dataset', 'value']}
    }
]
