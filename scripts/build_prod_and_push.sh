#!/bin/bash
echo argument 1 is the version, about to push: 
echo 
echo    hub.sekhnet.ra/budget:$1
echo 
echo ok?
read fart
docker build -t hub.sekhnet.ra/budget:$1 .
docker push hub.sekhnet.ra/budget:$1
