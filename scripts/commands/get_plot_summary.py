import requests

HOST = "localhost"
PORT = 8000

r = requests.get('http://' + HOST + ':' + str(PORT) + '/api/v1/summary')

print(r.status_code)
print(r.json)