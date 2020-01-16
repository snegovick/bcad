#!/bin/bash

source bcad_build_paths.sh

pushd ext/

INSTALL_DIR="$(pwd)/usr"

echo "Checking occ build dir presence"
if [ ! -e ${OCC_BUILD_DIR} ]; then
    echo "No build dir, create"
else
    echo "Build dir exists, recreate"
    rm -rf ${OCC_BUILD_DIR}
fi
mkdir ${OCC_BUILD_DIR}

echo "Checking occ sources"
if [ ! -e ${OCC_NAME} ]; then
    echo "No unpacked sources, check archive"
    if [ ! -e ${OCC_ARC_NAME} ]; then
        echo "No archive, download"
        curl ${OCC740_URL} -o ${OCC_ARC_NAME}
    fi
    echo "Unpack occ sources"
    tar xf ${OCC_ARC_NAME}
fi

pushd ${OCC_BUILD_DIR}
echo "Configure occ cmake build"
cmake -DINSTALL_DIR=${INSTALL_DIR} -DUSE_VTK=yes -DUSE_RAPIDJSON=yes -DUSE_FREEIMAGE=yes -DUSE_FFMPEG=yes ../${OCC_NAME}
make -j $(nproc)
make install -j $(nproc)
popd

popd
