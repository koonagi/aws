# EC2
aws ec2 describe-instances --profile <your_profile_name> --output json --query "Reservations[].Instances[].{Name:Tags[?Key==`Name`].Value,InstanceId:InstanceId,InstanceType:InstanceType,LaunchTime:LaunchTime,State:State.Name,Platform:Platform}" | jq -r ".[] | [.Name[0],.InstanceType,.InstanceId,.LaunchTime,.State,.Platform] | @csv"

# EBS
aws ec2 describe-volumes --profile <your_profile_name> --output json --query "Volumes[].{VolumeId:VolumeId,Size:Size,State:State,VolumeType:VolumeType,Name:Tags[?Key==`Name`].Value,CreateTime:CreateTime}"| jq -r ".[]| [.VolumeId,.VolumeType,.Size,.State,.Name[0],.CreateTime]|@csv"

# EBS スナップショット
aws ec2 describe-snapshots --owner self --output json --profile <your_profile_name> --query "Snapshots[].{SnapshotId:SnapshotId,VolumeId:VolumeId,VolumeSize: VolumeSize,State:State,StartTime:StartTime,Description:Description}"|jq -r ".[]| [.SnapshotId,.VolumeId,.VolumeSize,.State,.StartTime]|@csv"

# Lambda
aws lambda list-functions --profile <your_profile_name> --query "Functions[].{FunctionName:FunctionName,Runtime:Runtime,Timeout:Timeout,MemorySize:MemorySize}" |jq -r ".[] | [.FunctionName,.Runtime,.MemorySize,.Timeout] | @csv"

# Glue Jobs
aws glue get-jobs --profile <your_profile_name> --query "Jobs[].{Name:Name,JobLanguage:DefaultArguments,Timeout:Timeout,MaxCapacity:MaxCapacity}"|jq -r ".[]| [.Name,.JobLanguage[\"--job-language\"],.Timeout,.MaxCapacity] | @csv"

# CloudWatch Logs
aws logs describe-log-groups --profile <your_profile_name> --query "logGroups[].{logGroupName:logGroupName,storedBytes:storedBytes,creationTime:creationTime}"| jq -r ".[]|[.logGroupName,.storedBytes,.creationTime] | @csv"

# CloudWatch Events
aws events list-rules --profile <your_profile_name> --query "Rules[].{Name:Name,State:State,ScheduleExpression:ScheduleExpression}"|jq -r ".[]|[.Name,.State,.ScheduleExpression] | @csv"

# S3
aws s3api list-buckets --profile <your_profile_name>  --query "Buckets[].{Name:Name,CreationDate:CreationDate}" | jq -r ".[]|[.Name,.CreationDate] | @csv"

# Stepfunctions
aws stepfunctions  list-state-machines --profile <your_profile_name> --query "stateMachines[].{name:name,creationDate:creationDate}"|jq -r ".[]|[.name,.creationDate] | @csv"

# Cost
aws ce get-cost-and-usage  --time-period Start=YYYY-MM-DD,End=YYYY-MM-DD  --granularity MONTHLY   --metrics "BlendedCost" "UnblendedCost" "UsageQuantity"  --group-by Type=DIMENSION,Key=SERVICE Type=TAG,Key=Environment  --profile <your_profile_name> --query "ResultsByTime[].Groups[].{Keys:Keys,BlendedCost:Metrics.BlendedCost.Amount}"|jq -r ".[]|[.Keys[0],.BlendedCost] | @csv"
