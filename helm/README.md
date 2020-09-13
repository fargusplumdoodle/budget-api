Helm Chart for budget
--------------------

### Test scripts
##### Run templates
`./scripts/template.sh`

##### Install test
Installs the chart in the 'budget-test' namespace
```
# Install the release
./scripts/test-install.sh

# Remember to uninstall when you are finished!
helm uninstall -n budget-test budget-test
```

# Deployment
```
# Copy the example
cp ./scripts/test-install.sh ./install.sh

# set your own values
vi ./install.sh

# install release
./install.sh
```

### Usage

| Name              | Usage             |
|-------------------|-------------------|
| budget.db.DB      | Database name     |
| budget.db.DB_USER | User for database |
| budget.db.DB_PASS | Password for database |
| budget.db.DB_HOST | Hostname of database |
| budget.django.SECRET_KEY | Secret key used by django |

*only uses port 5432 for postgres connections*
