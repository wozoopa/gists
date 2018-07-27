#!/bin/bash

REGIONS=$(aws ec2 describe-regions --region us-west-2 --query "Regions[].RegionName" --output text| tr "\t" "\n" | tr "\n" " ")


for region in $REGIONS
   do
      echo "Getting Custom VPC list in $region region:"
      aws ec2 describe-vpcs --filters Name=isDefault,Values=false --query "Vpcs[].VpcId" --region=${region}
   done
