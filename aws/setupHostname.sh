#!/bin/bash

# /usr/local/bin/setupHostname.sh
# this script is called from /etc/rc.local
# Setup hostname based on ec2-metadata
# Requirement: Internal domain in dhcp-options must be set, example to: domain.net
#
# Tested on AmzLinux instances
#

EC2_METADATA="/opt/aws/bin/ec2-metadata"
DEBUG="false"
LOG="/var/log/messages"
SCRIPT_NAME=$(/bin/basename $0)
HOSTNAME=$(${EC2_METADATA} -h | awk -F": " '{print $2}' | awk -F"." '{print $1}')
DOMAIN=$(${EC2_METADATA} -h | awk -F": " '{print $2}' | cut -d"." -f2,3)
LOCKFILE="/var/lock/${SCRIPT_NAME}.lck"
OPTION="$1"
HOSTS_FILE="/etc/hosts"
NETWORK_CONFIG_FILE="/etc/sysconfig/network"

if [[ $EUID -ne 0 ]]; then
   echo "Please run this script as root or using sudo"
   exit 2
fi

Warning() {
   logger -t "${SCRIPT_NAME}"  "Warning: $1 Process aborted"
   exit 1
}

if [ -e "${LOCKFILE}" ]; then
   Warning "lock file exists"
else
   NEWHOSTNAME="${HOSTNAME}.${DOMAIN}"
   CHECK_FQDN=$(hostname -f 2>&1 | awk -F": " '{print $NF}')
UpdateHostname() {
   touch ${LOCKFILE}
   IP_ADDRESS=$(${EC2_METADATA} -o | awk -F": " '{print $2}')
   cp ${HOSTS_FILE} ${HOSTS_FILE}.bkp
   FIRSTLINE="127.0.0.1   localhost localhost.localdomain"
   echo -e "${FIRSTLINE} \n${IP_ADDRESS} \t ${NEWHOSTNAME}" >${HOSTS_FILE}
   cp ${NETWORK_CONFIG_FILE} ${NETWORK_CONFIG_FILE}.bkp
   sed -i -e "s/HOSTNAME=*.*/HOSTNAME=${NEWHOSTNAME}/g" ${NETWORK_CONFIG_FILE}
   hostname ${NEWHOSTNAME}
   service network restart
   rm -rf ${LOCKFILE}
}

   if [[ "$CHECK_FQDN" == "Unknown host" ]]; then
      UpdateHostname
   elif [[ "${CHECK_FQDN}" == "No address associated with name" ]]; then
      UpdateHostname
   elif [[ "${CHECK_FQDN}" == "Host name lookup failure" ]]; then
	  UpdateHostname
   elif [[ "${OPTION}" == "force" ]]; then
      UpdateHostname
   else
      echo "FQDN is already configured."
   fi
fi
