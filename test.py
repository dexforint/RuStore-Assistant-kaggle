def get_answer(prompt: str, temperature=0.6):
    headers = {
        "Authorization": "Api-Key AQVNz9fpuAtA5fGeDB_rcMEY_byJDgEEPeivMMYn",
        "Content-Type": "application/json",
    }

    json_data = {
        "modelUri": "gpt://b1g72uajlds114mlufqi/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": "2000",
        },
        "messages": [
            {
                "role": "system",
                "text": """Ты — умный ассистент. Твоя задача - полноценно ответить на вопрос пользователя, опираясь на предоставленные данные. В качестве входных данных тебе будут служить: вопрос пользователя, история переписки с пользователем и найденные материалы из справочной базы данных. Дай ответ исключительно в формате HTML без использования тегов <html>, <head>, <body>, а с использованием: <p>, <div>, <a>, <img>, <span>, <b>, <i>. Приложи ссылки источников справочных данных. Если ответ на вопрос пользователя отсутствует в справочных данных, то ничего не выдумывай, а так и напиши, что не знаешь ответа на данный вопрос.
Пример запроса пользователя:
```
Я не могу найти чек о покупке
```                
Пример ответа:
```
<p>Чтобы найти чек о покупке вам нужно выполнить несколько действий:</p>
<ol>
<li>Выберите приложение.<br/> Откроется карточка приложения с информацией о счёте.</li>
</ol>
<img alt="img" src="https://www.rustore.ru/help/assets/images/purchase-details-8aec791cf71288fbadad77848ce9e0fa.webp"/>
<ol>
<li>Нажмите «Получить чек».</li>
<li>Во всплывающем окне нажмите <img alt="img" src="/images/168.png"/> напротив нужного приложения, чтобы перейти на страницу с информацией о чеке.</li>
</ol>
<img alt="img" src="/images/169.png"/>
<br/>
Ресурсы: <a href="https://www.rustore.ru/help/users/purchases-and-returns/payment-history">1</a>
```
""",
            },
            {
                "role": "user",
                "text": prompt,
            },
        ],
    }

    response = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers=headers,
        json=json_data,
    )

    answer = response.json()["result"]["alternatives"][0]["message"]["text"]

    return answer


import requests

headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
}

params = {
    "model_id": "23",
    "prompt": "Привет",
}

response = requests.post(
    "https://api.qewertyy.dev/models", params=params, headers=headers
)

print(response.json()["content"][0]["text"])
