#!/bin/bash

sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-get update
sudo apt-get install -y openjdk-8-jdk

sudo apt-get install -y git libaudit-dev auditd libfuse-dev fuse pkg-config lsof uthash-dev
git clone https://github.com/ashish-gehani/SPADE.git
cd SPADE
git checkout tags/tc-e3
./configure
make
sudo chmod ug+s `which auditctl`
sudo chown root lib/spadeAuditBridge
sudo chmod ug+s lib/spadeAuditBridge
sudo sed -i "s/active = no/active = yes/" /etc/audisp/plugins.d/af_unix.conf
sudo service auditd restart

## Neo4j - need a specific package repo
wget -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.org/repo stable/' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install -y neo4j
sudo apt-get install -y cypher-shell
sudo apt-get install -y realpath
sudo apt-get install -y Graphviz
sudo apt-get install -y trace-cmd

## ProvMark stuff
cd ~
git clone https://github.com/arthurscchan/ProvMark.git
