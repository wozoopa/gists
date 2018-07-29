#!/bin/bash

REGIONS=$(aws ec2 describe-regions --region us-west-2 --query "Regions[].RegionName" --output text| tr "\t" "\n" | tr "\n" " ")


echo "Listing non default VPC's"
for region in $REGIONS
   do
      echo "Getting Custom VPC list in $region region:"
      aws ec2 describe-vpcs --filters Name=isDefault,Values=false --query "Vpcs[].{id:VpcId,cidr:CidrBlock}" --region=${region} --output table | sed -e '1,2d'
   done

echo -e "-----\n------"

echo "Listing default VPCS:"
for region in $REGIONS
   do
      echo "Getting Custom VPC list in $region region:"
      aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query "Vpcs[].{id:VpcId,cidr:CidrBlock}" --region=${region} --output table | sed -e '1,2d'
   done
