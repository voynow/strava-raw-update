import utils.secrets_manager as secrets_manager

# get secrets from secrets manager
secrets = secrets_manager.get_secrets()

# unpack secrets
client_id = secrets['client_id']
client_secret = secrets['client_secret']
email = secrets['email']
password = secrets['password']

streams_url_keys = "time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth"


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


def get_request_urls(activity_id):
    
    return {
        "zones": f'activities/{activity_id}/zones',
        "laps": f'activities/{activity_id}/laps',
        "streams": f'activities/{activity_id}/streams?keys={streams_url_keys}&key_by_type=true'
    }
