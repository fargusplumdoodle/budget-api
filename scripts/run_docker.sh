#!/bin/bash

docker rm -f budget 2> /dev/null
docker run -d \
    --rm \
    -p 80:8000 \
    -e DB_HOST=127.0.0.1 \
    -e DEBUG=TRUE\
    -e DB_USER="budget" \
    -e DB_PASS="budget" \
    -e DB="budget" \
    -e SECRET_KEY=zv0leozem7l-$v^vb5h8dlu*s!-+#dpr*cnid_z_9o5hk1abb8 \
    -v $(pwd):/code/ \
    --name budget \
    hub.sekhnet.ra/budget
