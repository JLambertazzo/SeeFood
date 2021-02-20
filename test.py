import requests
import uuid

BASE = "http://127.0.0.1:5000/"

# create two restaurants
response = requests.put(BASE + "api/restaurants", {
  "name": "my restaurant",
  "password": "mypassword",
  "description": "description of my restaurant"
})
other_response = requests.put(BASE + "api/restaurants", {
  "name": "my other restaurant",
  "password": "otherpassword",
  "description": "description of my restaurant"
})
rest_id = response.json()['id']
other_rest_id = other_response.json()['id']
print('successfully created' + rest_id + ' & ' + other_rest_id)

# update the restaurant
response2 = requests.patch(BASE + f"api/restaurants/{rest_id}", {
  "name": "updated restaurant",
  "description": "new updated description"
})
print(response2.json())

# try logging in as the restaurant
response21 = requests.get(BASE + "api/restaurants", {
  "name": "updated restaurant",
  "password": "mypassword"
})
print('login attempt gives us:' + response21.json()['id'])

# delete the restaurant
response3 = requests.delete(BASE + f"api/restaurants/{rest_id}")
print(response3.json())

# check if the restaurant is gone
response4 = requests.get(BASE + f"api/restaurants/{rest_id}")
print(response4.json())

print('==== END OF RESTAURANT TESTS ====')

# create meal
item_response = requests.put(BASE + f"api/item", {
  "restaurant": other_rest_id,
  "name": "a meal",
  "description": "a description",
  "ingredients": "an ingredient",
})
mid = item_response.json()['id']
print('successfully created ' + mid)

# update meal
item_response2 = requests.patch(BASE + f"api/item/{mid}", {
  "name": "an updated meal"
})
print(item_response2.json())

# check if still exists
item_response4 = requests.get(BASE + f"api/item/{mid}")
print(item_response4.json())

# # delete meal
# item_response3 = requests.delete(BASE + f"api/item/{mid}")
# print(item_response3.json())

# check if still exists
item_response4 = requests.get(BASE + f"api/item/{mid}")
print(item_response4.json())