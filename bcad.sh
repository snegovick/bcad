#!/bin/bash
LD_LIBRARY_PATH=$(pwd)/bcad/ext/usr/lib:${LD_LIBRARY_PATH} PYTHONPATH=$(pwd)/bcad/ext/usr/lib/python3/site-packages:$(pwd)/bcad/ext/usr/lib/python3.7/site-packages:${PYTHONPATH} python3.8 -m bcad.binterpreter.scl "$@"
