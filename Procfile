web: python main.py

If you want to use Gunicorn + UvicornWorker for better prod serving with async support:

web: gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --log-level info

> BUT if you do that, you need a separate worker for the bot or start bot before gunicorn pre-fork. A simpler single-process approach is to keep python main.py on free hosting.




---
