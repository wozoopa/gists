#!/bin/bash

# -------------------------------------- #
# Install code-deploy agent
# -------------------------------------- #

REGION=$(ec2-metadata -z | awk -F": " '{print $2}' | sed -e 's/.$//g')

wget https://aws-codedeploy-${REGION}.s3.amazonaws.com/latest/install
chmod +x install

