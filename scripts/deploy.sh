#!/bin/bash

# 0. Checking if version number was provided
if [[ $# -ne 1 ]]
then
	echo "Error: Version required as first argument"
	exit -1
fi

PROD_HOST=docker.sekhnet.ra
PROJECT_DIR_ON_HOST=docker/budget/
RUN_SCRIPT=docker/budget/run_prod.sh
BUILD_DIR=deploy/
PROJECT_NAME=budget

#  REQUIRED ARGUMENT!! $1 = VERSION
VERSION=$1
BUILD_FILE=$PROJECT_NAME-$VERSION.tar
BUILD_FILE_PATH=$BUILD_DIR$BUILD_FILE


# 1. Running Build
echo 1. Running Build
bash scripts/build.sh > /dev/null

# 2. Saving tar archive
echo 2. Saving tar archive
docker save $PROJECT_NAME > $BUILD_FILE_PATH

# 3. Rsyncing over to host
echo 3. Sending archive to $PROD_HOST
rsync -azvh -e ssh $BUILD_FILE_PATH $PROD_HOST:$PROJECT_DIR_ON_HOST$BUILD_FILE

# 4. Loading tar on host
echo 4. Loading archive on $PROD_HOST
ssh $PROD_HOST "docker load < $PROJECT_DIR_ON_HOST$BUILD_FILE"

# 5. Running productions script
echo 5. Running production script on $PROD_HOST
ssh $PROD_HOST "$RUN_SCRIPT"
