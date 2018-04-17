#!/usr/bin/env bash
WORKDIR=/root/cloudtree
if [ ! -e ${WORKDIR} ]; then
    mkdir ${WORKDIR}
fi
cd ${WORKDIR}

apt-get -y update

# clone project
echo Clone projects
git clone https://github.com/RicterZ/cloudtree
cd cloudtree

# install required software
echo Install requirements ...
apt-get -y install gcc git python-pip libmysqld-dev mrbayes libargtable2-dev

# install clustal omega
echo Install Clustal Omega
wget http://www.clustal.org/omega/clustal-omega-1.2.4.tar.gz
tar xvzf clustal-omega-1.2.4.tar.gz
pushd clustal-omega-1.2.4
./configure --with-pic --with-openmp
make && make install
popd

# install python libs
echo Installing python libs ...
pip install -r requirements.txt

chmod +x bin/celery_starter
ln -s ${WORKDIR}/config.py worker/config.py

nohup bin/celery_starter &
