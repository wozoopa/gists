#!/bin/bash

echo 'Setting hostname via user-data script'
hostname_prefix='<application>'
domain_name='<domain.something>'

instance_id=`/usr/bin/curl -s http://169.254.169.254/latest/meta-data/instance-id`
local_ip=`/usr/bin/curl -s http://169.254.169.254/latest/meta-data/local-ipv4`

short_name="$hostname_prefix-$instance_id"
fqdn="$hostname_prefix-$instance_id.$domain_name"

echo "$local_ip    $short_name $fqdn" >> /etc/hosts
/bin/sed -i "s/HOSTNAME=.*/HOSTNAME=$fqdn/" /etc/sysconfig/network
/bin/hostname $short_name
/bin/domainname $domain_name
/sbin/service network restart

echo 'user-data script complete'
