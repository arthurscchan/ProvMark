#!/bin/bash

sudo add-apt-repository ppa:webupd8team/java -y
sudo apt-get update
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections
sudo apt-get install -y oracle-java8-installer
sudo apt-get install -y oracle-java8-set-default

sudo apt-get install -y git libaudit-dev auditd libfuse-dev fuse pkg-config lsof uthash-dev
git clone https://github.com/ashish-gehani/SPADE.git
cd SPADE
./configure
make
sudo chmod ug+s `which auditctl`
sudo chown root lib/spadeAuditBridge
sudo chmod ug+s lib/spadeAuditBridge
sudo sed -i "s/active = no/active = yes/" /etc/audisp/plugins.d/af_unix.conf
sudo service auditd restart


## ProvMark stuff
# 
git clone https://github.com/arthurscchan/ProvMark.git 
