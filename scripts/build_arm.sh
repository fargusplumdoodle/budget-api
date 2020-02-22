#!/bin/bash
export DOCKER_BUILDKIT=1
export DOCKER_CLI_EXPERIMENTAL=enabled


docker buildx build \
	--platform linux/arm \
	-t budget:armhf .

if [ $? -ne 0 ];
then
	echo << EOF
EYYY! Something went wrong! Darn!

You may not have your system configured to build arm images!
 Checkout this webpage FOOL
	https://www.docker.com/blog/getting-started-with-docker-for-arm-on-linux/
	EOF
fi
