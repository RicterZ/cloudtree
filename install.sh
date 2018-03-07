#!/usr/bin/env bash
PROJECT_DIR=$(pwd)
TMP=/tmp/cloudtree
mkdir ${TMP} && cd ${TMP}

# install required software
echo Install requirements ...
sudo apt-get -y install openmpi-bin openmpi-doc libopenmpi-dev autoconf \
                        gcc unzip default-jdk git libargtable2-0 libargtable2-dev \
                        python-pip

# install beagle-lib
echo Installing beagle-lib ...
wget https://github.com/beagle-dev/beagle-lib/archive/master.zip -O beagle-lib.zip && unzip beagle-lib.zip
pushd beagle-lib-master
autoreconf -i
./configure
make
cp ./libhmsbeagle/.libs/libhmsbeagle.so.1 /usr/lib/
popd

# install mrbayes
echo Install mrbayes ...
wget https://svwh.dl.sourceforge.net/project/mrbayes/mrbayes/3.2.5/mrbayes-3.2.5.tar.gz
tar xvzf mrbayes-3.2.5.tar.gz
pushd mrbayes_3.2.5/src/
./configure --with-beagle --enable-mpi=yes
make
popd

# install python libs
echo Installing python libs ...
pip install idigbio
pip install celery
pip install flask
pip install sqlalchemy



sudo apt-get install rabbitmq-server