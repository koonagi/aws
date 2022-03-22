import json
import os
import boto3
import pprint as pp
from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

events_client = boto3.client('events')
events_name = 'website_monitor'

# Line API利用に必要な変数設定
channel_access_token = os.environ['token']
line_bot_api = LineBotApi(channel_access_token)


# ステータスの確認
def get_status(events_name):
    state = events_client.describe_rule(
            Name=events_name
            )['State']
            
    # print(state)
    return '現在のステータスは、"{}" です。'.format(state)

# イベントの起動
def start_events(events_name):
    response = events_client.enable_rule(
    Name=events_name
    )
    # print(response)
    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return 'Successful Start'
    else:
        print(response)
        return 'Some error occurred.'

# イベントの停止
def stop_events(events_name):
    response = events_client.disable_rule(
    Name=events_name
    )
    
    # print(response)
    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return 'Successful Stopped'
    else:
        print(response)
        return 'Some error occurred.'

# メッセージの返信
def reply_message(msg,reply_token):
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=msg))


# Main
def lambda_handler(event, context):
    
    event_body = json.loads(event['body'])
    
    print(event['body'])
    msg = event_body['events'][0]['message']['text'].lower()
    reply_token = event_body['events'][0]['replyToken']
    
    print(msg)
    print(reply_token)
    
    '''
    チャットルームに入力させた値によって分岐
    
    ・start : Eventsを起動
    ・stop : Eventsを停止
    ・status : Eventsのステータスを取得
    ・上記以外: Usageを表示
    '''
    
    if msg == 'start':
        msg = start_events(events_name)
        reply_message(msg,reply_token)
    elif msg == 'stop':
        msg = stop_events(events_name)
        reply_message(msg,reply_token)
    elif msg == 'status':
        msg = get_status(events_name)
        # msg = '現在のステータスは、"{}" です。'.format(state)
        reply_message(msg,reply_token)
    else:
        msg = '--Usage-- \nチャットに以下のキーワードを入力してください。\n\n ・起動: start \n ・停止: stop \n ・状態確認：status'
        reply_message(msg,reply_token)

    
  
    
