FROM python:3.10-alpine

COPY requirements.txt ./
RUN pip install -r ./requirements.txt --user

COPY . /app
WORKDIR /app

CMD ["python", "-m", "gunicorn", "-b", "0.0.0.0:5050", "messaging_api:create_app()"]