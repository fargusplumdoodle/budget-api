#!/bin/bash
docker build -t hub.sekhnet.ra/budget:staging .
docker push hub.sekhnet.ra/budget:staging
