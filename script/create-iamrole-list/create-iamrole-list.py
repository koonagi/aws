import boto3
import json
import pprint as pp
import pandas as pd
from IPython.display import display

#クライアントの生成
client = boto3.client('iam')

#IAMRole一覧の取得
responce = client.list_roles()
Roles = responce['Roles']

#IAMRole名とARNの取得
list_rolename = []
list_rolearn = []

for items in Roles:
    list_rolename.append(items['RoleName'])
    list_rolearn.append(items['Arn'])


#Role名よりアタッチされているIAMポリシーの取得
list_customerpolicy = []
list_managedpolicy = []

for items in Roles:
    customerpolicy = client.list_role_policies(
    RoleName=items['RoleName']
    )
    
    managedpolicy = client.list_attached_role_policies(
    RoleName=items['RoleName']
    )
    
    
    if managedpolicy['AttachedPolicies']:
        join_managedpolicy = []
        for i, policy in enumerate(managedpolicy['AttachedPolicies']):
            join_managedpolicy.append(policy['PolicyName'])
        list_managedpolicy.append(",".join(join_managedpolicy))
        list_customerpolicy.append(",".join(customerpolicy['PolicyNames']))
        continue
    list_customerpolicy.append(",".join(customerpolicy['PolicyNames']))
    list_managedpolicy.append(" ".join(managedpolicy['AttachedPolicies']))

#データフレームに入れるためのリスト
informations = []
informations.append(list_rolename)
informations.append(list_rolearn)
informations.append(list_customerpolicy)
informations.append(list_managedpolicy)

#データフレーム化
df = pd.DataFrame({
    'RoleName' : informations[0],
    'RoleArn' : informations[1],
    'CustomerPolicyName' : informations[2],
    'ManagedPolicyName' : informations[3]
    }
)

#DFの表示
display(df)

#CSVに出力
df.to_csv("IAMRoleList.csv")
