import requests
import uuid

BASE = "http://127.0.0.1:5000/"

# create a restaurant
response = requests.put(BASE + "api/restaurants", {
  "name": "my restaurant",
  "description": "description of my restaurant"
})
print(response.json())
print(str(uuid.uuid1()))