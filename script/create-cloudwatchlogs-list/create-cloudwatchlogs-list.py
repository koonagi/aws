import boto3
import pprint as pp
import csv

###################################
# MAIN処理
###################################

#--- 認証情報/環境識別子
access_key  = ''
secret_access = ''
region_name = 'ap-northeast-1'
env = 'dev'

#--- クライアントの生成
logs_client = boto3.client('logs',
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_access,
                      region_name=region_name)

######################################
# CloudWatchLogs 一覧情報の取得
######################################

logs_list = []
res = logs_client.describe_log_groups()

#--- Cloudwatchlogsにリテンションが設定されている場合リストに入れる
for i in res['logGroups']:
    if 'retentionInDays' in i:
        logs_list.append([i['logGroupName'], i['storedBytes'], i['retentionInDays']])
    else:
        logs_list.append([i['logGroupName'], i['storedBytes']])

#--- nextTokenが存在する場合の処理
while 'nextToken' in res:
    res = logs_client.describe_log_groups(nextToken=res['nextToken'])
    for i in res['logGroups']:
        if 'retentionInDays' in i:
            logs_list.append([i['logGroupName'], i['storedBytes'],i['retentionInDays']])
        else:
            logs_list.append([i['logGroupName'], i['storedBytes']])

 
######################################
# CSV出力
######################################

with open(env + '-cloudwatchlogs_list.csv', 'w') as file:
    header = ['logGroupName', 'storedBytes','retentionInDays']
    writer = csv.writer(file, lineterminator='\n')
    writer.writerow(header)
    writer.writerows(logs_list)

print('CSV creation completed : ' + env + '-cloudwatchlogs_list.csv')
