#!/bin/bash

#Retrieve OPUS Package and Extract the TARBALL
echo "Warning: Please get a licensed OPUS copy and extract to any location"

## Basic dependency
sudo apt-get update
sudo apt-get -y install git

## Install OpenJDK 8
sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-get update
sudo apt-get install -y openjdk-8-jdk

## Neo4j - need a specific package repo
wget -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.org/repo stable/' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get -y install neo4j=2.2.4
sudo apt-get -y install realpath
sudo apt-get -y install trace-cmd
sudo apt-get -y install Graphviz
#sudo apt-get -y install cypher-shell

## ProvMark stuff
cd ~
git clone https://github.com/arthurscchan/ProvMark.git 
cd ProvMark
git checkout Middleware2019
