#!/bin/bash

source bcad_build_paths.sh

pushd ext/

INSTALL_DIR="$(pwd)/usr"

echo "Checking pyocc build dir presence"
if [ ! -e ${PYOCC_BUILD_DIR} ]; then
    echo "No build dir, create"
else
    echo "Build dir exists, recreate"
    rm -rf ${PYOCC_BUILD_DIR}
fi
mkdir ${PYOCC_BUILD_DIR}

echo "Checking pyocc sources"
if [ ! -e ${PYOCC_GIT} ]; then
    echo "No sources, clone"
    if [ ! -e ${PYOCC_GIT} ]; then
        echo "No git, download"
        git clone ${PYOCC_GIT_URL}
    fi
fi

pushd ${PYOCC_BUILD_DIR}
echo "Configure pyocc cmake build"
PATH=${INSTALL_DIR}/bin:${PATH} cmake -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR} -DPYTHONOCC_INSTALL_DIRECTORY=${INSTALL_DIR}/lib/python3/site-packages/OCC -DOpenCASCADE_DIR=${INSTALL_DIR}/lib/cmake/opencascade -DPython3_ROOT_DIR=${INSTALL_DIR} ../${PYOCC_GIT}
make -j $(nproc)
make install -j $(nproc)
popd

popd
