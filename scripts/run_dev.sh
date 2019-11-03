#!/bin/bash

docker rm -f budget 2> /dev/null
docker run -d \
	--rm \
    -p 80:8000 \
    -e DB_HOST=10.0.1.60 \
    -e DEBUG=TRUE\
    -e DEV_USER="budget_dev" -e DEV_DB="budget_dev" -e DEV_PASS="c1fePqZrMcZJ2O5DFRvJaw==" \
    -e SECRET_KEY=zv0leozem7l-$v^vb5h8dlu*s!-+#dpr*cnid_z_9o5hk1abb8 \
    --name budget \
    budget
