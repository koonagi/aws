# やったこと
EC2とLambdaにアタッチされているIAMロールとIAMポリシーをCSVで出力

【CSV カラム】

* IAM Role名
* IAM Role ARN
* Inline Policy
* Managed Policy

【処理の流れ】

1.  IAM Roleの一覧を取得  
2.  1. 取得したIAM Role名からアタッチされているIAM ポリシーを取得しDF化  
3.  DFをCSVで出力  

#LINK
