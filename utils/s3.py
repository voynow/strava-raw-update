
import boto3
import json
import pathlib


raw_bucket = "strava-raw"
s3 = boto3.resource('s3')


def get_activities():
    """
    Get activities JSON from raw bucket
    """
    activities = []
    for obj in s3.Bucket(raw_bucket).objects.all():
        if pathlib.Path(obj.key).stem.isnumeric():
            body_bytes = obj.get()['Body'].read()
            activities.append(json.loads(body_bytes))
    return activities