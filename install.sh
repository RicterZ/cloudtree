#!/usr/bin/env bash
WORKDIR=/root/cloudtree
mkdir ${WORKDIR}
cd ${WORKDIR}

# install required software
echo Install requirements ...
apt-get -y update
apt-get -y install gcc unzip default-jdk git  \
                   python-pip libmysqld-dev mrbayes

# clone project
git clone https://github.com/RicterZ/cloudtree
cd cloudtree

# install python libs
echo Installing python libs ...
pip install -r requirements.txt

# start services
nohup bin/celery_starter &
