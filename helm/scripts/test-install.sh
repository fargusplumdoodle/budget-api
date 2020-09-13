#!/bin/bash
RELEASE=budget-test

# fake values for testing

echo removing old
helm uninstall $RELEASE --namespace $RELEASE
echo installing new
helm install $RELEASE . \
	--namespace $RELEASE \
	--create-namespace \
	--set budget.db.DB_HOST=192.168.254.254 \
	--set budget.db.DB_USER=fargus \
	--set budget.db.DB_PASS=fargus \
	--set budget.db.DB=fargus \
	--set budget.django.SECRET_KEY=eyyy
