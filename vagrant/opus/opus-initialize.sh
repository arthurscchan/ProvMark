#!/bin/bash

sudo apt-get update

#Retrieve OPUS Package and Extract the TARBALL
echo "Warning: Please get a licensed OPUS copy and extract to any location"

## Neo4j - need a specific package repo
wget -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.org/repo stable/' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install -y neo4j
sudo apt-get install -y cypher-shell
sudo apt-get install -y git

## Install Java 8
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get -y upgrade
echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections 
echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
sudo apt-get -y install oracle-java8-installer

## ProvMark stuff
sudo apt-get install -y python3-pip 
sudo apt-get install -y realpath
sudo apt-get install -y trace-cmd
sudo pip3 install setuptools --upgrade
sudo pip3 install json_merger
git clone https://github.com/arthurscchan/ProvMark.git 
