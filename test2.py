import os
import requests

headers = {
    "Authorization": "Bearer "
    + "a5938d38d767068a4bdf1517c8944dafe515ae76970a501103668647e30410b9",
    "Content-Type": "application/json",
}

json_data = {
    "model": "Qwen/Qwen2-72B-Instruct",
    "messages": [
        {
            "role": "user",
            "content": "Привет!",
        },
    ],
}

response = requests.post(
    "https://api.together.xyz/v1/chat/completions", headers=headers, json=json_data
)

print(response.json()["choices"][0]["message"]["content"])
