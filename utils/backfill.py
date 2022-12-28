
import boto3
import json
import pathlib
import utils.strava_api as strava_api

s3 = boto3.resource('s3')
bucket_name = "strava-raw"

def s3_ls_activities():
    """ Get activities JSON from raw bucket
    """
    activities = []
    for obj in s3.Bucket(bucket_name).objects.all():
        if pathlib.Path(obj.key).stem.isnumeric():
            activity = obj.get()['Body'].read()
            activities.append(json.loads(activity))
    return activities


def update_s3_obj(table, new_data, key):
    """
    """
    for k, v in new_data.items():
        table[k] = v

    s3.Object(bucket_name, key).put(Body=json.dumps(table))


def details_backfill(table_name):
    """ 
    """
    key = f'{table_name}.json'
    s3_obj = s3.Object(bucket_name, key).get()['Body'].read()

    # get ids from existing table
    table = json.loads(s3_obj)
    table_ids = list(table.keys())

    # get list of all ids
    activities = s3_ls_activities()
    activity_ids = [str(activity['id']) for activity in activities]

    # backfill ids missing from table
    backfill_ids = [idx for idx in activity_ids if idx not in table_ids]    

    if backfill_ids:
        access_token = strava_api.auth().json()['access_token']
        data = strava_api.batch_get_request(table_name, backfill_ids, access_token)
        update_s3_obj(table, data, key)
    else:
        print("Exiting: No data to backfill")


def activities_backfill():
    """ collect individual activity objects from raw bucket and create a json "table" 
        for all activities joined together (indexed by id)
    """
    activities = s3_ls_activities()
    activities_dict = {activity['id']: activity for activity in activities}
    s3.Object(bucket_name, 'activities.json').put(Body=json.dumps(activities_dict))