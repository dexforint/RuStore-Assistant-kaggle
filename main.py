print("Импорт библиотек...")
from fastapi import FastAPI, File, Form, UploadFile, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from tools import pipeline, get_text_from_audio, get_text_from_image
from pydantic import BaseModel

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Разрешить все источники (в продакшене лучше указать конкретные домены)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

history = []


@app.get("/")
async def main(request: Request):
    global history
    history = []
    context = {"request": request, "ip": "http://localhost"}
    return templates.TemplateResponse(name="index.html", context=context)


@app.get("/images/{filename}")
async def get_image(filename: str):
    filepath = f"./images/{filename}"

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(filepath)


@app.post("/reset_history")
async def reset_history():
    global history
    history = []
    return {"message": "History reset"}


class Message(BaseModel):
    query: str


@app.post("/query/")
async def query(message: Message):
    global history

    query = message.query

    answer = pipeline(query, history)

    return {"answer": answer}


#     return {
#         "answer": """<p><img decoding="async" loading="lazy" src="https://www.rustore.ru/help/assets/images/0e37d68e4b06a20cbfb1a28ffef808d3-4a33f7e8674decd4c7f1a4090bd97ebb.webp" title="500" width="980" height="1562" class="img_ev3q medium-zoom-image"><br>
# Скачать: <a href="https://www.rustore.ru/help/icons/logo-SVG.zip" target="_blank" rel="noopener noreferrer">SVG</a>, <a href="https://www.rustore.ru/help/icons/logo-PNG.zip" target="_blank" rel="noopener noreferrer">PNG</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Скачать: <a href="https://www.rustore.ru/help/icons/no-logo-SVG.zip" target="_blank" rel="noopener noreferrer">SVG</a>, <a href="https://www.rustore.ru/help/icons/no-logo-PNG.zip" target="_blank" rel="noopener noreferrer">PNG</a></p>"""
#     }


@app.post("/upload_audio")
async def upload_audio(audio: UploadFile = File(...)):
    try:
        # Создаем директорию для сохранения аудиофайлов, если она не существует
        os.makedirs("uploads", exist_ok=True)

        # Сохраняем аудиофайл
        file_path = f"uploads/{audio.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await audio.read())

        query = get_text_from_audio(file_path)
        answer = pipeline(query)

        return {"answer": answer}
    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}


@app.post("/upload_image")
async def upload_audio(image: UploadFile = File(...)):
    try:
        # Создаем директорию для сохранения аудиофайлов, если она не существует
        os.makedirs("uploads", exist_ok=True)

        # Сохраняем аудиофайл
        file_path = f"uploads/{image.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())

        query = get_text_from_image(file_path)
        answer = pipeline(query)

        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    print(f"Запуск...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # uvicorn main:app --reload
