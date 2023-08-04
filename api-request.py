import json
import requests
response = requests.get("http://localhost:8010/")
print(json.loads(response.text))