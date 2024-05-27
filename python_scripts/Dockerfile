# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 50505

ENV NAME World

CMD ["gunicorn", "--bind", "0.0.0.0:50505", "app:app"]
