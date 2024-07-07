import requests

headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
}

params = {
    "query": "Что такое RuStore?",
}

response = requests.post(
    "https://19k4wz0aa1xq.share.zrok.io/query", params=params, headers=headers
)

print(response.json())
