import requests

CLIENT_ID = '5a1e2b28b8a043b99d5a19ffb4d8a216'
CLIENT_SECRET = 'f31645c086aa4809a5fbaed43ef7ac30'

AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']