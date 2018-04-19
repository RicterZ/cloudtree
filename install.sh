#!/usr/bin/env bash
WORKDIR=/root/cloudtree
if [ ! -e ${WORKDIR} ]; then
    mkdir ${WORKDIR}
fi
cd ${WORKDIR}

# update source
apt-get -y update

# clone project
echo Clone projects ...
git clone https://github.com/RicterZ/cloudtree
cd cloudtree

# download
echo Download clustal-omega ...
if [ ! -e clustal-omega-1.2.4.tar.gz ]; then
    wget http://www.clustal.org/omega/clustal-omega-1.2.4.tar.gz
    tar xvzf clustal-omega-1.2.4.tar.gz
fi
pushd clustal-omega-1.2.4

# install required software
echo Install requirements ...
apt-get -y install gcc git python-pip libmysqld-dev libargtable2-dev
apt-get -y install gcc git python-pip libmysqld-dev libargtable2-dev

# install clustal omega
echo Install Clustal Omega
./configure --with-pic --with-openmp
make && make install
popd

# install python libs
echo Installing python libs ...
pip install -r requirements.txt

chmod +x bin/celery_starter
chmod +x worker/tree/vendor/megacc
ln -s ${WORKDIR}/config.py worker/config.py

nohup bin/celery_starter &
