#!/bin/bash
docker build -t hub.sekhnet.ra/budget-api:staging .
docker push hub.sekhnet.ra/budget-api:staging
