# これは何  
特権IAMポリシーに関するIAMリソースへのアタッチ及びデタッチを拒否するIAMポリシー。

制御アクション
* IAM User への特権IAMポリシーのアタッチ、デタッチ
* IAM Role への特権IAMポリシーのアタッチ、デタッチ
* IAM Group への特権IAMポリシーのアタッチ、デタッチ

制御対象特権IAMポリシー
* AdministratorAccess
* PowerUserAccess
 
# Usage
特権IAMポリシーを操作させたくない、IAMユーザーやIAMグループ、IAMロールに対して、このIAMポリシーをアタッチする。

# Link
https://www.cloudnotes.tech/entry/iam-policy-deny
