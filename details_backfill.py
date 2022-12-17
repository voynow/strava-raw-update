import boto3
import json
import pathlib
import utils.strava as strava


s3 = boto3.resource('s3')
bucket_name = "strava-raw"
details_tables = ["zones", "laps", "streams"]


def get_activities():
    """ Get activities JSON from raw bucket
    """
    activities = []
    for obj in s3.Bucket(bucket_name).objects.all():
        if pathlib.Path(obj.key).stem.isnumeric():
            body_bytes = obj.get()['Body'].read()
            activities.append(json.loads(body_bytes))
    return activities


def backfill(subset=None, tables=details_tables):
    """ 
    """
    activities = get_activities()
    activity_ids = [activity['id'] for activity in activities]
    
    if subset:
        activity_ids = activity_ids[:subset]
    
    access_token = strava.auth().json()['access_token']
    for table in tables:
        data = strava.batch_get_request(table, activity_ids, access_token) 
        s3.Object(bucket_name, f'{table}.json').put(Body=json.dumps(data))


backfill(subset=10)
