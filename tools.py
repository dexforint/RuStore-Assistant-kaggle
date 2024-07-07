import faiss
import torch
import pickle
import requests

from transformers import AutoTokenizer, AutoModel


# from faster_whisper import WhisperModel
# asr_model = WhisperModel("large-v3", device="cuda", compute_type="float16")
# import easyocr
# reader = easyocr.Reader(["en", "ru"])


device = "cuda" if torch.cuda.is_available() else "cpu"

index = faiss.read_index("./data/faiss.bin")

with open("./data/chunks.pickle", "rb") as file:
    chunks = pickle.load(file)

tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large")
model = AutoModel.from_pretrained("intfloat/multilingual-e5-large").to(device)


def average_pool(
    last_hidden_states: torch.Tensor, attention_mask: torch.Tensor
) -> torch.Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


def get_embedding(text, prefix="query: "):
    text = f"{prefix}{text}"

    batch_dict = tokenizer(
        [text], max_length=512, padding=True, truncation=True, return_tensors="pt"
    )
    for key, value in batch_dict.items():
        batch_dict[key] = value.to(device)

    outputs = model(**batch_dict)
    embs = average_pool(outputs.last_hidden_state, batch_dict["attention_mask"])

    embs = embs.detach().cpu().numpy()

    return embs


def find_similar_chunks(text: str):
    vec = get_embedding(text)

    similarities, indices = index.search(vec, 3)

    target_chunks = []
    for i in indices[0].tolist():
        target_chunks.append(chunks[i])

    return target_chunks


def get_prompt(query: str, target_chunks: list, history: str = None):
    html_str = "\n------\n".join(
        [
            f"Ресурс:{chunk['url']}\nСекция:\n{chunk['section']}\nHTML:\n{chunk['html']}"
            for chunk in target_chunks
        ]
    )

    history = history[-2:]

    history = [f"{el['author']}:\n```{el['text']}```" for el in history]
    history = "\n------\n".join(history)

    prompt = f"""Вопрос пользователя:
```    
{query}
```

Найденные справочные данные:
```
{html_str}
```

История:
{history}
"""

    return prompt


sys_prompt = """Ты — умный ассистент на русском языке. Твоя задача - полноценно ответить на вопрос пользователя, опираясь на предоставленные данные. В качестве входных данных тебе будут служить: вопрос пользователя, история переписки с пользователем и найденные материалы из справочной базы данных. Дай ответ исключительно в формате HTML без использования тегов <html>, <head>, <body>, а с использованием: <p>, <div>, <a>, <img>, <span>, <b>, <i>. Приложи ссылки на источники справочных данных. Если ответ на вопрос пользователя отсутствует в справочных данных, то ничего не выдумывай, а так и напиши, что не знаешь ответа на данный вопрос.
"""
# Пример запроса пользователя:
# ```
# Я не могу найти чек о покупке
# ```
# Пример ответа:
# ```
# <p>Чтобы найти чек о покупке вам нужно выполнить несколько действий:</p>
# <ol>
# <li>Выберите приложение.<br/> Откроется карточка приложения с информацией о счёте.</li>
# </ol>
# <img alt="img" src="https://www.rustore.ru/help/assets/images/purchase-details-8aec791cf71288fbadad77848ce9e0fa.webp"/>
# <ol>
# <li>Нажмите «Получить чек».</li>
# <li>Во всплывающем окне нажмите <img alt="img" src="/images/168.png"/> напротив нужного приложения, чтобы перейти на страницу с информацией о чеке.</li>
# </ol>
# <img alt="img" src="/images/169.png"/>
# <br/>
# Ресурсы: <a href="https://www.rustore.ru/help/users/purchases-and-returns/payment-history">1</a>
# ```

#  a5938d38d767068a4bdf1517c8944dafe515ae76970a501103668647e30410b9


def get_answer(prompt: str, temperature=0.6):
    prompt = sys_prompt + "\n\n" + prompt
    print(prompt)
    print(len(prompt))

    headers = {
        "Authorization": "Bearer "
        + "a5938d38d767068a4bdf1517c8944dafe515ae76970a501103668647e30410b9",
        "Content-Type": "application/json",
    }

    json_data = {
        "model": "Qwen/Qwen2-72B-Instruct",  # "Qwen/Qwen2-72B-Instruct",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    response = requests.post(
        "https://api.together.xyz/v1/chat/completions", headers=headers, json=json_data
    )

    return response.json()["choices"][0]["message"]["content"]


def pipeline(query: str, history=None):
    target_chunks = find_similar_chunks(query)
    prompt = get_prompt(query, target_chunks, history=history)
    answer = get_answer(prompt)

    history.append({"author": "user", "text": query})
    history.append({"author": "assistant", "text": answer})

    return answer


def get_text_from_audio(audio_path: str):
    segments, info = asr_model.transcribe(audio_path, beam_size=5, language="ru")

    query = []
    for segment in segments:
        query.append(segment.text)

    query = " ".join(query)
    return query


def get_text_from_image(image_path: str):
    # Распознавание текста
    results = reader.readtext(image_path)

    # Группировка результатов
    grouped_results = []
    current_group = []

    for i, (bbox, text, prob) in enumerate(results):
        if not current_group:
            current_group.append(text)
        else:
            prev_bbox = results[i - 1][0]
            current_bbox = bbox

            # Проверка, находится ли текущий бокс близко к предыдущему
            if is_close(prev_bbox, current_bbox):
                current_group.append(text)
            else:
                grouped_results.append(" ".join(current_group))
                current_group = [text]

    # Добавление последней группы
    if current_group:
        grouped_results.append(" ".join(current_group))

    return grouped_results


def is_close(bbox1, bbox2, threshold=20):
    """Проверка, находятся ли два бокса близко друг к другу"""
    _, _, _, y1 = bbox1[3]
    x2, y2, _, _ = bbox2[0]

    return abs(y1 - y2) < threshold
