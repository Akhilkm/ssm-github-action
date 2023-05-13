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
import boto3

client = boto3.client('ssm')

response = client.send_command(
    Targets=[{'Key': 'tag:Name', 'Values': ['akhil-test']}],
    DocumentName='AWS-RunShellScript',
    TimeoutSeconds=123,
    Comment='deploy',

    Parameters={"commands":["ls -al; sleep 60;  echo \"hello\""],"workingDirectory":["/home/ec2-user/"],"executionTimeout":["123"]},
    CloudWatchOutputConfig={'CloudWatchLogGroupName': 'akhil-test', 'CloudWatchOutputEnabled': True}
)
