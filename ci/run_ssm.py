import os
import boto3
import subprocess
import time
import signal

client = boto3.client('ssm')
region = os.getenv('AWS_REGION')

try:
    response = client.send_command(
        # Targets=[{"Key":"tag:deploy","Values":["ssm"]}],
        InstanceIds=[]
        DocumentName='AWS-RunShellScript',
        TimeoutSeconds=600,
        Comment='deploy',

        Parameters={"workingDirectory":["/home/ec2-user/"],"commands":["#!/bin/bash","","echo \"downloading build from s3\"","rm -rf dist*","aws s3 cp s3://github-actions-build/build/dist.zip .","echo \"unzipping dist.zip\"","unzip dist.zip","echo \"removing old dist\"","rm -rf /usr/share/nginx/html/dist","echo \"copy new dist\"","cp -rf dist /usr/share/nginx/html/","echo \"listing files in blush_dist\"","ls -la /usr/share/nginx/html","echo \"finding size of blush_dist\"","du -s /usr/share/nginx/html/dist"],"workingDirectory":["/home/ec2-user/"]},
        # Parameters={"commands":["ls -al; sleep 60;  echo \"hello\""],"workingDirectory":["/home/ec2-user/"]},
        CloudWatchOutputConfig={'CloudWatchLogGroupName': 'akhil-test', 'CloudWatchOutputEnabled': True}
    )
except Exception as e:
        print(e)
        exit("ERROR: sending the run command")

print("Started SSM command with commandid:", response["Command"]["CommandId"])

print("\n\nlogs....\n\n")
time.sleep(2)
p = subprocess.Popen("awslogs get akhil-test --region ap-southeast-1 ALL --watch", shell=True)
while True:
    time.sleep(10)
    status = client.list_commands(CommandId=response["Command"]["CommandId"])['Commands'][0]["Status"]
    if status == 'InProgress' or status == 'Pending':
        continue
    elif status == "Failed":
        os.kill(p.pid, signal.SIGKILL)
        print("the job got failed, please contact the administrator")
        exit(1)
    elif status == "TimedOut":
        os.kill(p.pid, signal.SIGKILL)
        print("the job got timedout, please contact the administrator")
        exit(1)
    elif status == "Cancelling":
        os.kill(p.pid, signal.SIGKILL)
        print("the job is Cancelling, please contact the administrator")
        exit(1)
    else:
        os.kill(p.pid, signal.SIGKILL)
        print("the job is success, pelase check the functionality")
        exit(0)