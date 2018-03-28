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

## ProvMark stuff
sudo apt-get install python3-pip 
sudo apt-get install realpath
sudo pip3 install json_merger
git clone https://github.com/arthurscchan/ProvMark.git 
