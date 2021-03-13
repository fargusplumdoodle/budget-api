#!/bin/bash
docker build -t hub.sekhnet.ra/budget-api:dev .
docker push hub.sekhnet.ra/budget-api:dev
