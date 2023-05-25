#!/bin/bash

dateti=$(date '+%Y%m%d%H%M')
asgName='Blu-Prod-Mercury-ASG'
tagName=$(echo $asgName | sed 's/-ASG\|ASG//')
preprodTag=Blu-Prod-Mercury-Preprod
preProdId=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$preprodTag"  --output text --query 'Reservations[*].Instances[*].InstanceId')


############ AMI Create ########################

echo "AMI is creating ..."
ami_id=$(aws ec2 create-image --instance-id $preProdId --name "$tagName-ASI-$dateti" --description "$dateti" --query ImageId --output text)
(($? != 0)) && { printf '%s\n' "Error Occured exiting"; exit 1; } #if error exist the script to prevent further executions
aws ec2 create-tags --resources $ami_id --tags Key=Name,Value="$tagName-ASI-$dateti"   #tagging
ami_name=$(aws ec2 describe-images --image-ids $ami_id --query 'Images[].Name')
echo "creating Launch configuration ..."
aws autoscaling create-launch-configuration --launch-configuration-name $tagName-ASLC-$dateti --image-id $ami_id --cli-input-json file://$tagName-ASLC.json --user-data file://MercuryEc2UserData.sh
(($? != 0)) && { printf '%s\n' "Error Occured exiting"; exit 1; }  #if error exit the script to prevent further executions
sleep 5
lc_name=$(aws autoscaling describe-launch-configurations --launch-configuration-names $tagName-ASLC-$dateti --query 'LaunchConfigurations[*].LaunchConfigurationName')
lc_details=$(aws autoscaling describe-launch-configurations --launch-configuration-names $lc_name --query 'LaunchConfigurations[*].[LaunchConfigurationName,ImageId,CreatedTime]')
echo "Launch configuration is created.."
echo "$lc_details"
echo ""
echo "Updating Auto Scaling Group.."
aws autoscaling update-auto-scaling-group --auto-scaling-group-name $asgName --launch-configuration-name $lc_name
lc_verified_name=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names $asgName --query 'AutoScalingGroups[].LaunchConfigurationName')
echo "Auto scaling Group: $asgName  is updated with Launch configuration : $lc_verified_name"

######### Target Re-Register ###############

for tgarn in $(echo $tgarn_list);
do
        echo "Re-registerning Instance $instanceId from $tgarn"
        aws elbv2 register-targets --target-group-arn $tgarn --targets Id=$instanceId
done


#####deleteing Launch config , AMI and snapshot###################

oldest_lc=$(aws autoscaling describe-launch-configurations --query 'LaunchConfigurations[*].LaunchConfigurationName' --output json | grep $tagName  | tr -d '"| |,' | sort | head -n1)
if [ "$oldest_lc" != "$lc_verified_name" ];
    then
        delete_oldest_imageid=$(aws autoscaling describe-launch-configurations --launch-configuration-names $oldest_lc --query 'LaunchConfigurations[*].ImageId')
        delete_oldest_snapshotid=$(aws ec2 describe-images --image-ids $delete_oldest_imageid --query 'Images[].BlockDeviceMappings[].Ebs[].SnapshotId')

        echo "Deleting the oldest LC  => $oldest_lc"
        echo "Deleting the oldest AMI  => $delete_oldest_imageid"
        echo "Deleting the oldest Snapshot => $delete_oldest_snapshotid"
        aws autoscaling delete-launch-configuration --launch-configuration-name $oldest_lc
        (($? != 0)) && { printf '%s\n' "Error Occured exiting"; exit 1; } #if error exist the script to prevent further executions
        aws ec2 deregister-image --image-id $delete_oldest_imageid
        (($? != 0)) && { printf '%s\n' "Error Occured exiting"; exit 1; } #if error exist the script to prevent further executions
        aws ec2 delete-snapshot --snapshot-id $delete_oldest_snapshotid
        (($? != 0)) && { printf '%s\n' "Error Occured exiting"; exit 1; } #if error exist the script to prevent further executions

    else
        echo "You Cannot Delete Currently active LC"
fi


exit 0