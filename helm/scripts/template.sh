#!/bin/bash

# fake values for testing

helm template . \
	--set budget.db.DB_HOST=192.168.254.254 \
	--set budget.db.DB_USER=fargus \
	--set budget.db.DB_PASS=fargus \
	--set budget.db.DB=fargus \
	--set budget.django.DEBUG=TRUE \
	--set budget.django.SECRET_KEY=eyyy
