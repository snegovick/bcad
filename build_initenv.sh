#!/bin/bash

if [ ! -e ext ]; then
    echo "Creating ext directory"
    mkdir ext
fi
pushd ext
INSTALL_DIR="$(pwd)/usr"

echo "Checking install path presence"
if [ -e ${INSTALL_DIR} ]; then
    echo "usr is present, removing"
    rm -rf usr
fi

#virtualenv -p python3 usr
mkdir usr
echo "INSTALL_DIR: ${INSTALL_DIR}"

popd
