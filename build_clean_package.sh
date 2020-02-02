#!/bin/bash

if [[ -n $(git status --porcelain) ]]; then echo "repo is dirty"; git status --porcelain; exit 1; fi


echo "Running opencascade build"
bash ./build_opencascade.sh

echo "Running python-occ build"
bash ./build_pyocc.sh

echo "Building package"
bash ./packaging/build_deb.sh
