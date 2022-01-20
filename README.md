# Sekhnet Budget
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)

Very simple budgeting software I wrote
to keep track of my budgets

Sekhnet Budget is a Django based REST API that I deploy
on my local network at home using Kubernetes.

### How it works
Each budget is issued a percentage that represents
what portion of income should go to it. for example,
if housing is 30% and you add 1000$ of income, 300$ will
got to housing and the 700$ will be divided among the other
budgets

### Stability
I have been using version 1 for the last 10 months (as of this commit), running
it on my local kubernetes cluster. It has been working great for me.

I intend on using and updating this for the rest of my life
But note I will likely go significant periods of time without
updating it.

### API
Really basic API functionality has been added. Documentation can
be found in the Postman Collection located at `docs/Budget.postman_collection.json`

All the requests are prefixed with `/api/v2`


### Running locally

Setup environment with your database settings
```
docker-compose up
```

If you run into database issues, try this
```
python3 manage.py makemigrations
python3 manage.py migrate
```


### Deploying Sekhnet Budget API

If you have a Kubernetes cluster use the helm chart located in `./helm`

Or use docker compose if you prefer

## Prometheus metrics
Available from `/metrics`


# Patch notes
## v2.1
Date: 2020-10-31

Changes:
- Added Prometheus metrics
- Dates not match equal to

## v2
Date: 2020-09-19

Changes:
- All transaction amounts stored as cents with integers
- Advanced querying for transactions
- CRUD for budgets and transactions
- income function can now be set with any description/date
- Removed web interface, client will now be flutter based
- Removed graph history function
- Added helm chart for installing on a Kubernetes cluster
- Added docker-compose for easier development
- Updated Postman collection for API calls

## v1
Date: 2019-11-03

Changes:
- All transaction amounts stored as dollars with floats
- Very limited front end built with django templates
- Graph history functionality
- Most data assumed to be entered/modified through admin interface
- income function to split money into each budget based on its percentage
- Postman collection for API calls
