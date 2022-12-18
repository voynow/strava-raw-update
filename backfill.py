import boto3
import json
import pathlib
import utils.strava as strava


s3 = boto3.resource('s3')
bucket_name = "strava-raw"
details_tables = ["zones", "laps", "streams"]


def s3_ls_activities():
    """ Get activities JSON from raw bucket
    """
    activities = []
    for obj in s3.Bucket(bucket_name).objects.all():
        if pathlib.Path(obj.key).stem.isnumeric():
            activity = obj.get()['Body'].read()
            activities.append(json.loads(activity))
    return activities


def activities_backfill():
    """ collect individual activity objects from raw bucket and create a json "table" 
        for all activities joined together (indexed by id)
    """
    activities = s3_ls_activities()
    activities_dict = {activity['id']: activity for activity in activities}
    s3.Object(bucket_name, 'activities.json').put(Body=json.dumps(activities_dict))


def append_new_data(new_data, table):
    add_idxs = []
    for idx in new_data:
        if idx not in table:
            add_idxs.append(idx)

    for idx in add_idxs:
        table[idx] = new_data[idx]
    return table


def update_s3_obj(table_name, new_data):
    
    key = f'{table_name}.json'
    s3_obj = s3.Object(bucket_name, key).get()['Body'].read()

    table = append_new_data(
        json.dumps(new_data), 
        json.loads(s3_obj)
    )

    s3.Object(bucket_name, key).put(Body=table)



def details_backfill(idxs=None, tables=details_tables):
    """ 
    """
    activities = s3_ls_activities()
    activity_ids = [activity['id'] for activity in activities]
    
    if idxs:
        activity_ids = activity_ids[idxs[0]:idxs[1]]
    
    access_token = strava.auth().json()['access_token']
    for table in tables:
        data = strava.batch_get_request(table, activity_ids, access_token)
        update_s3_obj(table, data)


details_backfill(idxs=[0, 1], tables=[details_tables[2]])
