source .venv/bin/activate 

uvicorn api:app --reload

python3 telegram_bot.py