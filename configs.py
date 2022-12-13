import secrets_manager

# get secrets from secrets manager
secrets = secrets_manager.get_secrets()

# unpack secrets
client_id = secrets['client_id']
client_secret = secrets['client_secret']
email = secrets['email']
password = secrets['password']


# string format config
strfrmt = "%m/%d/%Y, %H:%M:%S"


def get_oauth_code_param():
    return f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri=http://localhost&response_type=code&scope=activity:read_all"


def get_oauth_url(code):
    return {
        "url": "https://www.strava.com/api/v3/oauth/token?",
        "params": {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": code,
        }
    }


def get_activities_url(access_token):
    return {
        "url": "https://www.strava.com/api/v3/athlete/activities",
        "params": {
            "header": {'Authorization': 'Bearer ' + access_token},
            "param": {'per_page': 200, 'page': 1}
        }
    }