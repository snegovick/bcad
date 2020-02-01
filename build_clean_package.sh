#!/bin/bash

if [[ -n $(git status --porcelain) ]]; then echo "repo is dirty"; git status --porcelain; exit 1; fi

echo "Running initenv"
bash ./build_initenv.sh

echo "Running opencascade build"
bash ./build_opencascade.sh

echo "Runnin python-occ build"
bash ./build_pyocc.sh
