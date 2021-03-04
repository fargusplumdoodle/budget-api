#!/bin/bash
RELEASE=budget

helm upgrade $RELEASE /code/helm \
	--namespace $RELEASE \
	--create-namespace \
	--set budget.db.DB_HOST=$PROD_DB_HOST \
	--set budget.db.DB_USER=$PROD_DB_USER \
	--set budget.db.DB_PASS=$PROD_DB_PASS \
	--set budget.db.DB=$PROD_DB \
	--set budget.django.SECRET_KEY=$PROD_SECRET_KEY
