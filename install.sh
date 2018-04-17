#!/usr/bin/env bash
PROJECT_DIR=$(pwd)
TMP=/tmp/cloudtree
mkdir ${TMP}
cd ${TMP}

# install required software
echo Install requirements ...
sudo apt-get -y install gcc unzip default-jdk git  \
                        python-pip libmysqld-dev mrbayes

# clone project
git clone https://github.com/RicterZ/cloudtree
cd cloudtree

# install python libs
echo Installing python libs ...
pip install -r requirements.txt
