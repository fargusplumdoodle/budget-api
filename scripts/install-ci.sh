#!/bin/bash
set -ex
apt update && apt install build-essential -y 

pip install -U pip pipenv
pipenv lock \
	--dev \
	--keep-outdated \
	--requirements > /requirements.txt 
pip install -U pip install -r /requirements.txt
