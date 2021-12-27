#!/bin/bash
set -ex
apt update && apt install build-essential -y 

python3.9 -m venv ./venv
./venv/bin/pip install -U pip pipenv
./venv/bin/pipenv lock \
	--dev \
	--keep-outdated \
	--requirements > /requirements.txt 
./venv/bin/pip install -U pip install -r /requirements.txt
