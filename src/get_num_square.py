# src/get_num_square.py
import os
import boto3

# get the input and convert it to int
num = os.environ.get("INPUT_NUM")
if num:
    try:
        num = int(num)
    except Exception:
        exit('ERROR: the INPUT_NUM provided ("{}") is not an integer'.format(num))
else:
    num = 1

s3_client = boto3.client('s3')


my_config = Config(
    region_name = 'ap-southeast-1',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)
objects = s3_client.list_objects_v2(Bucket='cloudbank-terraform-backend',  config=my_config)

for obj in objects['Contents']:
    print(obj['Key'])

# to set output, print to shell in following syntax
print(f"::set-output name=num_squared::{num ** 2}")