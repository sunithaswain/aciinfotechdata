#!/bin/bash
pip install virtualenv

virtualenv venv -p python3

os=${OSTYPE//[0-9.-]*/}

case "$os" in
  msys)
    source ./portal_venv/Scripts/activate
    ;;
  *)
    source ./portal_venv/bin/activate
    ;;
esac
# install the dependent libraries
python -m pip install -r requirements.txt
# install couchbase library for local setup
python -m pip install couchbase==2.5.4
# run the unit tests
python -m unittest discover -s unit-test -p '*_test.py' &>unittest.log
# install the app inside the packages
python -m pip install -e .
