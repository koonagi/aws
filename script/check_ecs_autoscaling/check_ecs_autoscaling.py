import boto3
import time
import pprint as pp
import json

#--- 変数定義
cluster_name = 'arn:aws:ecs:ap-northeast-1:xxxxxx:cluster/xxxxxxx'

#--- クライアント生成
ecs_client = boto3.client('ecs')
asg_client = boto3.client('autoscaling')
sns_client = boto3.client('sns')

#######################################
#
# DRAINING対象のインスタンスの特定し、コンテナインスタンスARN、ステータス、タスク実行数を返す
#
#######################################

def detect_draining_instance_target(target_instance_id):


    arns = ecs_client.list_container_instances(cluster=cluster_name)['containerInstanceArns']
    desc_resp = ecs_client.describe_container_instances(cluster=cluster_name,containerInstances=arns)
    
    for container_instance in desc_resp['containerInstances']:
        if target_instance_id == container_instance['ec2InstanceId']:
            return {
                        'container_instance_arn':container_instance['containerInstanceArn'],
                        'container_instance_status': container_instance['status'],
                        'container_instance_task_count': container_instance['runningTasksCount']
                    }

#######################################
#
# コンテナインスタンスをDRAININGに変更
#
#######################################

def draining_instance(container_instance_info):
    
    ecs_client.update_container_instances_state(cluster=cluster_name,containerInstances=[container_instance_info['container_instance_arn']],status='DRAINING')

#######################################
#
# Main
#
#######################################

def lambda_handler(event, context):
    
    #--- DRAINING対象のインスタンスIDの取得
    msg = json.loads(event['Records'][0]['Sns']['Message'])
    target_instance_id =  msg["detail"]['EC2InstanceId']
    
    
    #--- コンテナインスタンスARN,Status,タスクの実行数の取得
    container_instance_info = detect_draining_instance_target(target_instance_id)


    #---コンテナインスタンスがDRAININGでなかった場合、DRAININGに変更
    if container_instance_info['container_instance_status'] != 'DRAINING':
        draining_instance(container_instance_info)


    #---実行中のタスクがあるかチェック。実行中のタスクがある場合、SNSにメッセージを送信し、Lambdaを終了する。
    
    if container_instance_info['container_instance_task_count'] != 0:
        print('Tasks are running.Finish Lambda Function.')
        time.sleep(30)
        sns_resp = sns_client.publish(TopicArn=event['Records'][0]['Sns']['TopicArn'],
                             Message=json.dumps(msg),
                             Subject='Publishing SNS msg to invoke Lambda again.')
        return


    #---AutoScaling グループのライフライクルをResumeする
    print('Resume Lifecycle')
    asg_client.complete_lifecycle_action(LifecycleHookName= msg["detail"]['LifecycleHookName'],
                                AutoScalingGroupName= msg["detail"]['AutoScalingGroupName'],
                                LifecycleActionResult='CONTINUE',
                                InstanceId= msg["detail"]['EC2InstanceId'])
