#!/bin/bash

run_server() {
    mkdir -p ~/.aws
    echo "[default]" > ~/.aws/credentials

    MY_AWS_ACCESS_KEY_ID={ACCESS_KEY}
    MY_AWS_SECRET_ACCESS_KEY_ID={SECRET_ACCESS_KEY}
    MY_REGION=eu-central-1

    echo "aws_access_key_id = ${MY_AWS_ACCESS_KEY_ID}" >> ~/.aws/credentials
    echo "aws_secret_access_key = ${MY_AWS_SECRET_ACCESS_KEY_ID}" >> ~/.aws/credentials
    echo "[default]" > ~/.aws/config
    echo "output = json" >> ~/.aws/config
    echo "region = ${MY_REGION}" >> ~/.aws/config

    #Test access to AWS
    aws ec2 describe-instances >> /home/ec2-user/describe-instances.response

    #Download python script from S3 repo
    cd
    git clone https://github.com/authext/dsurv
    cd dsurv

    PATH="/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/opt/aws/bin:/home/ec2-user/.local/bin:/home/ec2-user/bin"
    pipenv --python $(which python3.4)
    pipenv install
    pipenv run python3.4 -m server.server_main --bucket titos-treasury-1234 > server.log 2> server.err.log

}
export -f run_server

yum update -y
yum install -y python34 python34-pip git
pip-3.4 install boto3 awscli pipenv

su ec2-user -c "bash -c run_server"
