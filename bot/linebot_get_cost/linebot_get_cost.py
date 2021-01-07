import os, sys
import boto3
import json
import calendar
from datetime import datetime, date
from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

ce_client = boto3.client('ce')

# Line API利用に必要な変数設定
user_id = os.getenv('LINE_USER_ID', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)


#--------------------
# 指定した期間のAWS利用料を返す関数
#--------------------
def get_aws_cost(start_day,end_day):
    
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': datetime.strftime(start_day, '%Y-%m-%d'),
                'End': datetime.strftime(end_day, '%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
        )
    except Exception as e:
        message = '[Error]' + '\n' + 'specify up to the past 12 months.'
        push_message(message)
        raise e

    
    return response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']


#--------------------
# 指定した年月の初日と最終日を返す関数
#--------------------
def get_frst_last_date(year,month):
    return calendar.monthrange(year, month)


#--------------------
# Lineに送信するメッセージを作成する関数
#--------------------

def create_message(start_day,end_day,aws_cost):

    message = '開始日: ' + start_day.strftime('%Y年%m月%d日') + '\n' + '終了日: ' + end_day.strftime('%Y年%m月%d日') + '\n' +'AWS利用料: $' + str(round(float(aws_cost),1))
    return message


#--------------------
# Lineにメッセージを送信する関数
#--------------------

def push_message(message):
    messages = TextSendMessage(text=message)
    line_bot_api.push_message(user_id, messages=messages)

#--------------------
# Main
#--------------------

def lambda_handler(event, context):
    
    # Lineに入力したテキストを変数に格納
    # YYYY MMを想定。それ以外は、月初から今日までのAWS利用料金の取得。
    args = json.loads(event['body'])['events'][0]['message']['text'].split(" ")
    
    print(args)
    
    if len(args) == 2:
        try:
            check_date_format = args[0] + args[1]
            datetime.strptime(check_date_format, '%Y%m')
            year = args[0]
            month = args[1]
        except ValueError:
            message = '[Error]' + '\n' + 'Incorrect data format, should be YYYY MM'
            push_message(message)
            raise ValueError(message)
    else:
        year = None
        month = None    
    
    # 変数YearとMonthがNullでなければ、指定した年月の月額利用料を取得する
    # Nullの場合は、月初から本日までの利用料を取得する
    if all(v is not None for v in [year,month]):
        
        # 指定した年月の月額利用料を取得する
        year_int = int(year)
        month_int = int(month)

        first_last_day = get_frst_last_date(year_int,month_int)
        start_day = date(year_int,month_int,1)
        end_day = date(year_int,month_int,first_last_day[1])
        aws_cost = get_aws_cost(start_day,end_day)
        
        # Line送信用メッセージの作成
        message = create_message(start_day,end_day,aws_cost)
        
        # Lineにメッセージ送信
        push_message(message)
        
        return
  
    #月初から今日までのAWS利用料金の取得
    today = datetime.today()
    first_day = today.replace(day=1)
    aws_cost = get_aws_cost(first_day,today)
    
    # Line送信用メッセージの作成
    message = create_message(first_day,today,aws_cost)

    # Lineにメッセージ送信
    push_message(message)
    
    return
