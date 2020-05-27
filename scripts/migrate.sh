#!/bin/bash

python3 manage.py makemigrations 
python3 manage.py makemigrations api

python3 manage.py migrate api
python3 manage.py migrate 
