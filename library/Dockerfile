FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY main.py .

EXPOSE $APP_PORT

CMD uvicorn main:app --reload --host $APP_HOST --port $APP_PORT
