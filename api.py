from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai import OpenAI

import os
from dotenv import load_dotenv
import pickle
import uuid
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = 'gpt-4o'
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)
# CORS configuration
origins = [
    "http://localhost:3000",  # React app URL
]

client = OpenAI(api_key=OPENAI_API_KEY)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str = None
    input: str

class ChatResponse(BaseModel):
    session_id: str = None
    response: str

def save_session(session_id, session_data):
    with open(os.path.join(SESSION_DIR, f"{session_id}.pkl"), 'wb') as f:
        pickle.dump(session_data, f)

def load_session(session_id):
    try:
        with open(os.path.join(SESSION_DIR, f"{session_id}.pkl"), 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {'messages': []}
    

@app.get("/init", response_model=ChatResponse)
async def init():
    session_id = str(uuid.uuid4())

    session_data = {"messages": [
        {"role": "system", "content": """
            You are assisting the user with playing out various social scenarios. 
            You are to give the user a list of three options for social situations. 
            The user will respond with the scenario they want to roleplay. 
            You will prompt the user to make the first conversational move. You are then
            to go back and forth with the user for 10 messages. You then are to stop and give the user an evaluation for how well they performed in the scenario. You are to rate the user by ability to maintain a conversation, follow some sense of social norm and be engaging in the conversation. The goal is for the user to get good enough to make friends with strangers."""},
    ]}
    # Get response from OpenAI
    response = client.chat.completions.create(
        model=MODEL,
        messages=session_data["messages"],
    )
    assistant_response = response.choices[0].message.content

    # Add assistant response to session messages
    session_data["messages"].append({"role": "assistant", "content": assistant_response})

    # Save session data
    save_session(session_id, session_data)

    return ChatResponse(session_id=session_id, response=assistant_response)



@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    user_input = request.input

    session_data = load_session(session_id)
    session_data["messages"].append({"role": "user", "content": user_input})

    if session_data is None:
        session_data = {"messages": []}
    # Get response from OpenAI
    print('session_data', session_data)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": """
            You are assisting the user with playing out various social scenarios. 
            You are to give the user a list of three options for social situations. 
            The user will respond with the scenario they want to roleplay. 
            You will prompt the user to make the first conversational move. You are then
            to go back and forth with the user for 10 messages. You then are to stop and give the user an evaluation for how well they performed in the scenario. You are to rate the user by ability to maintain a conversation, follow some sense of social norm and be engaging in the conversation. The goal is for the user to get good enough to make friends with strangers."""},
            *session_data["messages"],
        ],
    )
    print(response)
    assistant_response = response.choices[0].message.content

    # Add assistant response to session messages
    session_data["messages"].append({"role": "assistant", "content": assistant_response})

    # Save session data
    save_session(session_id, session_data)

    return ChatResponse(session_id=session_id, response=assistant_response)



@app.get("/")
async def root():
    return {"message": "Welcome to the ChatGPT API!"}
