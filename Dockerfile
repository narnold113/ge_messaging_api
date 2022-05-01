FROM python:3.10-alpine

COPY requirements.txt ./
RUN pip install -r ./requirements.txt

COPY . /app
WORKDIR /app

CMD ["gunicorn", "-b", "0.0.0.0:5050", "messaging_api:create_app()"]