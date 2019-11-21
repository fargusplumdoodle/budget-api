# DATABASE REVISIONS !

This file contains a list of database revisions


2019-Oct: Initial
--------
This was the initial deployment

```python
class Budget(models.Model):
    name = models.TextField(max_length=20, unique=True)
    percentage = models.FloatField(max_length=100)
    initial_balance = models.FloatField(max_length=4000, null=True)
    
class Transaction(models.Model):
    amount = models.FloatField(max_length=4000)
    description = models.TextField(max_length=300, null=True)
    budget = models.ForeignKey(Budget, null=True, on_delete=models.SET_NULL)
    date = models.DateField(auto_now_add=True)
```
2019-11-10
------
Allowing date to be changed
NOTE: this didnt work
```python
    date = models.DateField(auto_now=True)
```

2019-11-20
------
- Allowing date to be changed
- removed config table. It was never used
```python
    date = models.DateField()
```
