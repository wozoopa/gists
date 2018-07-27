#!/bin/bash

KUBE_REPO_FILE="/etc/yum.repos.d/kubernetes.repo"
K8CONFIG="/etc/sysctl.d/k8s.conf"

Usage() {
    echo "Please run this script as root or using sudo"
    exit 2
}


InstallKubernetes() {
yum install docker -y

systemctl enable docker
systemctl start docker

echo -e "[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg" >> $KUBE_REPO_FILE


setenforce 0
perl -pi.orig -e 's/enforcing/permissive/g' /etc/selinux/config
yum install kubelet kubeadm kubectl -y
systemctl enable kubelet
systemctl start kubelet

echo -e "/etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1" >> $K8CONFIG

sysctl --system
}


if [[ ${EUID} -ne "0" ]]; then
    Usage
else
    InstallKubernetes
fi
