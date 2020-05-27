#!/bin/bash
docker rm -f postgres-dev
docker run \
	-p 5432:5432 \
	--name postgres-dev \
	--restart unless-stopped \
	-e POSTGRES_PASSWORD=budget \
	-e POSTGRES_USER=budget \
	-e POSTGRES_DB=budget \
	-d postgres
