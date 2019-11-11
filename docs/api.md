# API

Graph History
---------
Warning: very resource intensive query,
         it is quite poorly designed

Endpoint: api/v1/graph/history

#### Request:
Must have:
- start date: str, format below 

        Restrictions:
        min="2019-10-01" max="2077-07-31"

- end date: str, format below

        Restrictions:
        min="2019-10-01" max="2077-07-31"

- budgets: list of budget names, must exist in db. 

       
```json
{
  'start': '2019-11-10',
  'end': '2019-12-12',
  'budgets': [
      'food',
      'personal'
  ],
}
```
####Response:
Status: 200
```json
{
    'days':['2019-10-11 00:21:30.307150', ...],
    'budgets': [
            {
              'name': 'budget_name',
             'data': [125, 167, 35, ...],
             }
            
            ...
    ]
}
```
#### Error Response
If there is an issue with the request, the error response will be in 
this format 

Status code: 400
```json
{"error": "description of error}
```
