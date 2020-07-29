import boto3
import datetime as dt
import json
import pprint as pp

#--- クライアント生成
ecs_client = boto3.client('ecs')
ssm_client = boto3.client('ssm')

#--- 変数定義
accountid = <your_aws_account_name>                # Account ID
paramater_store_name = <your_paramater_store_name> #パラメータストア名


#######################################
# 停止対象のタスクリストの洗い出し
#######################################

def check_task_timeout(cluster_arn,task_arns,timeout,task_def_name):
    
    del_list = []
    
    for task_arn in task_arns:

        response = ecs_client.describe_tasks(
            cluster=cluster_arn,
            tasks= [task_arn]
            )
        
        res_task_def_name = response['tasks'][0]['taskDefinitionArn'].split('/')[1].split(':')[0]
        deltatime  = dt.datetime.now() - response['tasks'][0]['createdAt'].replace(tzinfo=None)
        
        if deltatime.seconds//3600 >= timeout and task_def_name == res_task_def_name:
            del_list.append(task_arn)
    
    return del_list
        

#######################################
# タスクの停止
#######################################

def stop_task(cluster_arn,del_list):
    
    
    for task_arn in del_list:
        response = ecs_client.stop_task(
        cluster=cluster_arn,
        task=task_arn,
        reason='Timeout exceeded'
        )
        

#######################################
# Main
#######################################

def lambda_handler(event, context):

    # パラメータストアよりパラメータの取得(json形式)
    param = ssm_client.get_parameter(Name=paramater_store_name)["Parameter"]["Value"]
    param_json = json.loads(param)

    # クラスター/タスク定義ごとにコンテナのタイムアウトチェック
    for cluster_name,values in param_json.items():
        for i in values:
            print('========================')
            cluster_arn = 'arn:aws:ecs:ap-northeast-1:{0}:cluster/{1}'.format(accountid,cluster_name)
            task_def_name = i['task_def_name']
            timeout = i['timeout']
            print("cluster name: " + cluster_name)
            print("cluster arn: " + cluster_arn)
            print("task def name: " + i['task_def_name'])
            print("timeout: " + str(i['timeout']))
    

            # タスク一覧取得
            task_arns = ecs_client.list_tasks(cluster=cluster_arn)['taskArns']
            print("Task List :" + str(task_arns) )
            
            
            # 停止対象のタスク一覧の取得
            del_list = check_task_timeout(cluster_arn,task_arns,timeout,task_def_name)
            print("Stop Task List :" + str(del_list) )
            if len(del_list) == 0:
                continue
                
            
            # タスクの停止
            stop_task(cluster_arn,del_list)
