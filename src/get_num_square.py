# src/get_num_square.py
import os
import boto3

# get the input and convert it to int
# num = os.environ.get("INPUT_NUM")
# if num:
#     try:
#         num = int(num)
#     except Exception:
#         exit('ERROR: the INPUT_NUM provided ("{}") is not an integer'.format(num))
# else:
#     num = 1


s3 = boto3.resource('s3', region_name='ap-southeast-1')
for bucket in s3.buckets.all():
  print(bucket.name)

# # to set output, print to shell in following syntax
# print(f"::set-output name=num_squared::{num ** 2}")