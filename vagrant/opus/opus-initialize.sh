#!/bin/bash

## Basic dependency
sudo apt-get update
sudo apt-get -y install git

## Install OpenJDK 8
sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-get update
sudo apt-get install -y openjdk-8-jdk
export JAVA_INCLUDE_DIR=/usr/lib/jvm/java-8-openjdk-amd64/include/
export C_INCLUDE_PATH=/usr/lib/jvm/java-8-openjdk-amd64/include/:/usr/lib/jvm/java-8-openjdk-amd64/include/linux/
export CPLUS_INCLUDE_PATH=$C_INCLUDE_PATH:/usr/lib/jvm/java-8-openjdk-amd64/include/linux/

## Neo4j - need a specific package repo
wget -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.org/repo stable/' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get -y install neo4j=2.2.4
sudo apt-get -y install realpath
sudo apt-get -y install trace-cmd

## OPUS
#sudo apt-get -y install python-pip python-dev build-essential unzip
#cd ~
#git clone https://github.com/DTG-FRESCO/opus
#cd opus
#./build.sh

## ProvMark stuff
cd ~
git clone https://github.com/arthurscchan/ProvMark.git 
cd ProvMark
git checkout Middleware2019

##
echo "You must obtain you own copy of OPUS from https://github.com/DTG-FRESCO/opus and install it in the virtual machine manually."
