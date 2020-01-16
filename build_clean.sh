#!/bin/bash

pushd ext
set +e
set -x
rm -rf occ_build
rm -rf pyocc_build
rm -rf opencascade-7.4.0
rm opencascade-7.4.0.tgz
rm -rf pythonocc-core
set +x
set -e
popd
