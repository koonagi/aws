import boto3
import pprint as pp
import pandas as pd
from IPython.display import display

#======================
# IAMロール名を渡すとIAMポリシーを返す関数
#======================

def check_iam_policy(role_name_list):
    inlinepolicy_list = []
    managedpolicy_list = []

    pp.pprint(role_name_list)

    for i in role_name_list:
        if i != 'No Role':

            inlinepolicy = iam_client.list_role_policies(
                RoleName=i
            )

            managedpolicy = iam_client.list_attached_role_policies(
                RoleName=i
            )

            if managedpolicy['AttachedPolicies']:
                join_managedpolicy = []
                for i, policy in enumerate(managedpolicy['AttachedPolicies']):
                    join_managedpolicy.append(policy['PolicyName'])
                managedpolicy_list.append(",".join(join_managedpolicy))
                inlinepolicy_list.append(",".join(inlinepolicy['PolicyNames']))
                continue
            inlinepolicy_list.append(",".join(inlinepolicy['PolicyNames']))
            managedpolicy_list.append(" ".join(managedpolicy['AttachedPolicies']))
            continue

        inlinepolicy_list.append(' ')
        managedpolicy_list.append(' ')

    return inlinepolicy_list,managedpolicy_list

#======================
# 行分のサービス名を格納したリストを返す関数
#======================

def create_service_name_list(name,count):
    service_name = [name for i in range(len(count))]
    return service_name

#======================
# データフレームを作成する関数
#======================

def create_dataframe(service_name,name_tag,role_name,customer_policy,managed_policy):

    #データフレームに入れるためのリスト
    informations = []
    informations.append(service_name)
    informations.append(name_tag)
    informations.append(role_name)
    informations.append(customer_policy)
    informations.append(managed_policy)

    #データフレーム化
    return pd.DataFrame({
        'AWSService Name': informations[0],
        'Name': informations[1],
        'Role Name' : informations[2],
        'Inlinepolicy Name' : informations[3],
        'ManagedPolicy Name' : informations[4]
        }
    )


###################################
# MAIN処理
###################################

access_key = 'xxxxxxxxxxxx'
secret_access = 'xxxxxxxxxxxxxxxxxx'
region_name = 'ap-northeast-1'

# クライアントの生成
iam_client = boto3.client('iam',
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_access,
                      region_name=region_name)

ec2_client = boto3.client('ec2',
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_access,
                      region_name=region_name)

iam_resource = boto3.resource('iam',
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_access,
                      region_name=region_name)


lambda_client = boto3.client('lambda',
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_access,
                      region_name=region_name)


######################################
# EC2 一覧情報 / アタッチされているIAMロール及びIAMポリシーの取得
######################################

ec2_name_list = []
role_name_list = []
instance_profile_name_list = []


# EC2 一覧の取得
res = ec2_client.describe_instances()

for i in res['Reservations']:
    # 変数の初期化
    ec2_name = None
    instance_profile_name = None

    # EC2のNameタグを取得する。 Nameタグがない場合は、'No Name Tag'とする。
    tags = i['Instances'][0]['Tags']

    for tag in tags:
        if tag['Key'] == 'Name':
            ec2_name = tag['Value']

    if ec2_name is None:
        ec2_name = 'No Name Tag'

    # EC2にアタッチされているInstanceProfile情報を取得。アタッチされていない場合は、"No Instance Profile"。
    if 'IamInstanceProfile' in i['Instances'][0]:
        # 取得したInstanceProfile情報を成形してInstanceProfile名を取得する
        instance_profile_name = i['Instances'][0]['IamInstanceProfile']['Arn'].split(':')[5].replace('instance-profile/','')

    if instance_profile_name is None:
        instance_profile_name = 'No Instance Profile'

    # EC2名とアタッチされているInstanceProfile情報をリストに格納。
    ec2_name_list.append(ec2_name)
    instance_profile_name_list.append(instance_profile_name)


# IAMロール名を取得する。
for i in instance_profile_name_list:
    # 変数の初期化
    role_name = None

    # InstanceProfile名からIAM ロール名を取得する。 IAM ロールがアタッチされていないインスタンスについては、”No Role”とする。
    if i != 'No Instance Profile':
        role_name = str(iam_resource.InstanceProfile(i).roles[0]).split('\'')[1].strip('\'')

    if role_name != None:
        role_name_list.append(role_name)
        continue

    role_name = 'No Role'
    role_name_list.append(role_name)

# IAMロールに紐づくIAMポリシー取得
policy_list = check_iam_policy(role_name_list)

# DataFrame作成
service_name_list = create_service_name_list('ec2',ec2_name_list)
ec2_df = create_dataframe(service_name_list,ec2_name_list,role_name_list,policy_list[0],policy_list[1])



######################################
# Lambda 一覧情報 / アタッチされているIAMロール及びIAMポリシーの取得
######################################

# リストの初期化
service_name_list = []
role_name_list = []
policy_list = []
lambda_name_list = []

res = lambda_client.list_functions()

# Lambda名 及び 紐づくIAMロール名の取得
for i in res['Functions']:
    lambda_name_list.append(i['FunctionName'])
    role_name_list.append(i['Role'].split(':')[5].replace('service-role/','').replace('role/',''))

#  一度に取得できるLambda数が50件のため、50件以降のデータを取得する処理
while 'NextMarker' in res:
    res = lambda_client.list_functions(Marker=res['NextMarker'])
    for i in res['Functions']:
        lambda_name_list.append(i['FunctionName'])
        role_name_list.append(i['Role'].split(':')[5].replace('service-role/','').replace('role/',''))
    print('next!')

# IAMロールに紐づくIAMポリシー取得
policy_list = check_iam_policy(role_name_list)

# DataFrame作成
service_name_list = create_service_name_list('lambda',lambda_name_list)
lambda_df = create_dataframe(service_name_list,lambda_name_list,role_name_list,policy_list[0],policy_list[1])


######################################
# CSVへの出力
######################################

# AWS サービスごとのDataFrameのマージ
all_df = pd.concat([ec2_df, lambda_df], axis=0)

# インデックスの振り直し
display(all_df.reset_index(drop=True))

# CSVに出力
all_df.reset_index(drop=True).to_csv("IAMRoleList.csv")
