#!/bin/bash

##Basic dependency
sudo apt-get update
sudo apt-get install -y git libaudit-dev auditd libfuse-dev fuse pkg-config lsof uthash-dev

##OpenJDK 8
wget https://download.java.net/openjdk/jdk8u40/ri/openjdk-8u40-b25-linux-x64-10_feb_2015.tar.gz
sudo mkdir /usr/lib/jvm
sudo tar xvf openjdk-8u40-b25-linux-x64-10_feb_2015.tar.gz --directory /usr/lib/jvm
rm -f /home/vagrant/openjdk-8u40-b25-linux-x64-10_feb_2015.tar.gz
export PATH="$PATH:/usr/lib/jvm/java-se-8u40-ri/bin:/usr/lib/jvm/java-se-8u40-ri/db/bin/:/usr/lib/jvm/java-se-8u40-ri/jre/bin"
export J2SDKDIR="/usr/lib/jvm/java-se-8u40-ri"
export J2REDIR="/usr/lib/jvm/java-se-8u40-ri/jre"
export JAVA_HOME="/usr/lib/jvm/java-se-8u40-ri"
export DERBY_HOME="/usr/lib/jvm/java-se-8u40-ri/db"
sudo update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/java-se-8u40-ri/bin/javac 0
sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-se-8u40-ri/bin/java 0

##SPADE
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
git checkout Middleware2019
