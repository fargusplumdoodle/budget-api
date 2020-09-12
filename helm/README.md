Helm Chart for budget
--------------------

Test scripts:
`./scripts/template.sh`


Usage:

| Name              | Usage             |
|-------------------|-------------------|
| budget.db.DB      | Database name     |
| budget.db.DB_USER | User for database |
| budget.db.DB_PASS | Password for database |
| budget.db.DB_HOST | Hostname of database |
| budget.django.DEBUG | If this is set to "TRUE", django will run in DEBUG mode |
| budget.django.SECRET_KEY | Secret key used by django |
|                   |                   |
|                   |                   |
|                   |                   |

*only uses port 5432 for postgres connections*
