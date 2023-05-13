import os
import boto3
import subprocess
import time
import signal

client = boto3.client('ssm')


try:
    response = client.send_command(
        Targets=[{'Key': 'tag:Name', 'Values': ['akhil-test']}],
        DocumentName='AWS-RunShellScript',
        TimeoutSeconds=600,
        Comment='deploy',

        Parameters={"workingDirectory":["/home/ec2-user/"],"commands":["#!/bin/bash","","runtime=\"5 minute\"","endtime=$(date -ud \"$runtime\" +%s)","","while [[ $(date -u +%s) -le $endtime ]]","do"," echo \"Time Now: `date +%H:%M:%S`\""," echo \"Sleeping for 10 seconds\""," sleep 10","done"]},
        # Parameters={"commands":["ls -al; sleep 60;  echo \"hello\""],"workingDirectory":["/home/ec2-user/"]},
        CloudWatchOutputConfig={'CloudWatchLogGroupName': 'akhil-test', 'CloudWatchOutputEnabled': True}
    )
except Exception as e:
        print(e)
        exit("ERROR: sending the run command")

print("Started SSM command with commandid:", response["Command"]["CommandId"])

print("\n\nlogs....\n\n")
p = subprocess.Popen("awslogs get akhil-test --region ap-southeast-1 ALL --watch", shell=True)
while True:
    time.sleep(10)
    status = client.list_commands(CommandId=response["Command"]["CommandId"])['Commands'][0]["Status"]
    if status == 'InProgress' or status == 'Pending':
        print("still running")
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