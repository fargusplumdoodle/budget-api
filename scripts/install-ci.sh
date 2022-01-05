#!/bin/bash
set -ex
python -m venv ./venv
./venv/bin/pip install -U pip pipenv
./venv/bin/pipenv lock \
	--dev \
	--keep-outdated \
	--requirements > /requirements.txt 

