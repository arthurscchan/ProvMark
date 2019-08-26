#!/bin/bash

sudo apt-get update

#Retrieve OPUS Package and Extract the TARBALL
echo "Warning: Please get a licensed OPUS copy and extract to any location"

## Neo4j - need a specific package repo
wget -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.org/repo stable/' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install neo4j=2.2.4
#sudo apt-get -y install cypher-shell
sudo apt-get -y install git

## Install OpenJDK 8
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

## ProvMark stuff
sudo apt-get -y install python3-pip 
sudo apt-get -y install realpath
sudo apt-get -y install trace-cmd
sudo apt-get -y install Graphviz
sudo pip3 install setuptools --upgrade
sudo pip3 install json_merger
git clone https://github.com/arthurscchan/ProvMark.git 
cd ProvMark
git checkout Middleware2019
