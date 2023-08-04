uvicorn app.api:app --host 0.0.0.0 --port 8010 --reload --reload-dir tagifai --reload-dir app  # dev
gunicorn -c app/gunicorn.py -k uvicorn.workers.UvicornWorker app.api:app  # prod