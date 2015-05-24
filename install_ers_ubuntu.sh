#!/bin/bash -e
#PREPARATION

OPENSMILE_URL=http://sourceforge.net/projects/opensmile/files/opensmile-2.0-rc1.tar.gz
OPENSMILE_TAR=${OPENSMILE_URL##*/}
OPENSMILE_DIR=opensmile-2.0-rc1

DBNAME=ers_backend_db
DBUSER=root
DBPASS=root

# Add repository for ffmpeg
sudo add-apt-repository ppa:kirillshkrogalev/ffmpeg-next

# Update packages
sudo apt-get update
sudo apt-get -y upgrade

#MYSQL
sudo apt-get -y install libmysqlclient-dev mysql-server

MYSQL=`which mysql`

Q1="CREATE DATABASE IF NOT EXISTS $DBNAME;"
Q2="GRANT ALL ON *.* TO '$DBUSER'@'localhost' IDENTIFIED BY '$DBPASS';"
Q3="FLUSH PRIVILEGES;"
SQL="${Q1}${Q2}${Q3}"

echo "Enter MySQL password"
$MYSQL -uroot -p -e "$SQL"

#GIT
sudo apt-get -y install git

# REDIS
sudo apt-get -y install redis-server

# Python
sudo apt-get -y install python-pip python-dev build-essential

sudo pip install --upgrade pip

#INSTALL REQUIREMENTS
sudo pip install -r requirements.txt

# OpenCV
sudo apt-get -y install python-software-properties
sudo apt-get -y install software-properties-common

sudo apt-get install -y python python-dev python-pip python-virtualenv ffmpeg
sudo apt-get install -y python-opencv
sudo apt-get -y install python-numpy python-matplotlib
sudo apt-get -y install sox

#OPENSMILE
sudo apt-get -y install automake autoconf libtool gcc g++ m4 gnuplot
wget $OPENSMILE_URL
tar -zxvf $OPENSMILE_TAR
cd $OPENSMILE_DIR/opensmile
./autogen.sh
./autogen.sh
./configure
make
make
sudo make install
sudo ldconfig
SMILExtract -h

cd ../..
rm -rf $OPENSMILE_TAR $OPENSMILE_DIR

#FRONTEND
sudo apt-get -y install nodejs-legacy npm
sudo npm install -g bower

cd ers_frontend
sudo npm install
bower install


