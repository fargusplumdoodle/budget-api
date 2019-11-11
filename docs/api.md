# API

Graph History
---------
Warning: very resource intensive query,
         it is quite poorly designed

Endpoint: api/graph/history

#### Request:

Must have:
- start date: str, format below

- end date: str, format below

- budgets: list of budget names, must exist in db. 

- all_budgets: bool

If "all_budgets" is true, value of 'budgets'
is ignored and all budgets are included in output.

       
```json
{
  'start': '2019-11-10',
  'end': '2019-12-12',
  'budgets': [
      'food',
      'personal'
  ],
  'all_budgets': false
  
}
```
####Response:
```json
{
    'days':['2019-10-11 00:21:30.307150', ...],
    'budgets': {
            'budget_name': [125, 167, 35, ...],
            ...
    }
}
```
