from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

load_dotenv()

OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = 'gpt-4o'

openai.api_key = OPEN_API_KEY

app = FastAPI()


class ChatRequest(BaseModel):
    input: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request.input},
        ],
    )
    return ChatResponse(response=response.choices[0].message["content"])


@app.get("/")
async def root():
    return {"message": "Welcome to the ChatGPT API!"}
