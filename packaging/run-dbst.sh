#!/bin/bash

#sudo debootstrap  unstable debian-arm64 http://ftp.debian.org/debian
#fakechroot
packages="python3-dev,python3-pyqt5,python3-pyqt5.qtopengl,python3-ply,python3-setuptools,cython3,python3-numpy,python3-watchdog,python3-pyinotify,python3-sip,python3-six"
echo "Install packages ${packages}"
export PATH=/usr/sbin:/sbin:$PATH
fakechroot fakeroot debootstrap --foreign --keyring /usr/share/keyrings/debian-archive-keyring.gpg --include=${packages} --variant=fakechroot testing $1 http://ftp.debian.org/debian
DEBOOTSTRAP_DIR=$1/debootstrap fakechroot fakeroot debootstrap --second-stage --second-stage-target=$1
