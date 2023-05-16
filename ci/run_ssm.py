import os
import boto3
import subprocess
import time
import signal

client = boto3.client('ssm')
region = os.getenv('AWS_REGION')
branch = os.getenv('GITHUB_REF_NAME')
instance_id = os.getenv('INSTANCE_ID')
log_group_name = os.getenv('LOG_GROUP_NAME')

try:
    response = client.send_command(
        # Targets=[{"Key":"tag:deploy","Values":["ssm"]}],
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        TimeoutSeconds=600,
        Comment='deploy',

        Parameters={"workingDirectory":["/home/darren/"],"commands":["#!/bin/bash","su darren","source /home/darren/scripts/.env","echo \"Working Environment = $UMI_ENV\"","cd /opt/mer/blush","git fetch --all --tags","echo \"branch is \""+branch,"git checkout "+branch,"git branch","npm ci","npm run build","npm run test","exit 0"]},
        CloudWatchOutputConfig={'CloudWatchLogGroupName': log_group_name, 'CloudWatchOutputEnabled': True}
    )
except Exception as e:
        print(e)
        exit("ERROR: sending the run command")

print("Started SSM command with commandid:", response["Command"]["CommandId"])

print("\n\nlogs....\n\n")
time.sleep(2)
p = subprocess.Popen("awslogs get akhil-test --region {} ALL --watch".format(region), shell=True)
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