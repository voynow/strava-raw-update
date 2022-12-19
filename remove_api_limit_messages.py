import boto3
import json
import utils.configs as configs

s3 = boto3.resource('s3')
bucket_name = "strava-raw"


def exe():

    for table in configs.activities_endpoints:
        filename = f"{table}.json"

        data = json.loads(
            s3.Object(bucket_name, filename).get()['Body'].read())

        delete_keys = []
        for k, v in data.items():
            if 'message' in v:
                delete_keys.append(k)

        for k in delete_keys:
            del data[k]


        s3.Object(bucket_name, filename).put(Body=json.dumps(data))


exe()