release: python manage.py migrate --no-input
web: gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker threeNineTee.asgi:application
celeryworker: celery worker -A threeNineTee.celeryconf:app --loglevel=info -E
