FROM --platform=linux/amd64 python:3.10

RUN mkdir /app
COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:5050", "messaging_api:create_app()"]