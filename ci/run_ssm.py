import os
import boto3
import subprocess
import time
import signal

client = boto3.client('ssm')
branch = os.getenv('GITHUB_REF')
print("branch is ", branch)
region = os.getenv('AWS_REGION')
print(region)
print(os.getenv("TARGET_BRANCH"))

try:
    response = client.send_command(
        Targets=[{"Key":"tag:deploy","Values":["ssm"]}],
        DocumentName='AWS-RunShellScript',
        TimeoutSeconds=600,
        Comment='deploy',

        Parameters={"workingDirectory":["/home/ec2-user/"],"commands":["#!/bin/bash","","echo \"downloading build from s3\"","aws s3 cp s3://github-actions-build/build/dist.zip .","","unzip dist.zip","rm -rf /opt/mer/blush_dist/dist","cp -rf dist /opt/mer/blush_dist/","ls -la /opt/mer/blush_dist","du -s /opt/mer/blush_dist/dist"],"workingDirectory":["/home/ec2-user/"]},
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