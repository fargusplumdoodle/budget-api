# Deploying budget
Isaac Thiessen

Nov 3rd 2019

## Steps
0. READ THE SCRIPT ./scripts/deploy.sh
1. Set variables in ./scripts/deploy.sh
2. Ensure you have ssh public key access to the $PROD_HOST you specified
3. Check previous versions and decide what version you are making
4. Run ./scripts/deploy.sh <version_no> from the root directory of the project


## Procedure
 1. Run Build
 2. Save tar archive
 3. Rsync arvhice over to host
 4. Load tar on host (ssh)
 5. Run production script (ssh)
