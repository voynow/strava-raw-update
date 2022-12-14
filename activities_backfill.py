import boto3
import json
import pathlib


s3 = boto3.resource('s3')
bucket_name = "strava-raw"


def get_activities():
    """ Get activities JSON from raw bucket
    """
    activities = []
    for obj in s3.Bucket(bucket_name).objects.all():
        if pathlib.Path(obj.key).stem.isnumeric():
            body_bytes = obj.get()['Body'].read()
            activities.append(json.loads(body_bytes))
    return activities


def backfill():
    """ collect individual activity objects from raw bucket and create a json "table" 
        for all activities joined together (indexed by id)
    """
    activities = get_activities()
    activities_dict = {activity['id']: activity for activity in activities}
    s3.Object(bucket_name, 'activities.json').put(Body=json.dumps(activities_dict))


backfill()
