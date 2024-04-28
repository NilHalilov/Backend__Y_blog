FROM python:3.10.12

RUN apt-get update && apt-get install -y python3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /server/
RUN pip install -r /server/requirements.txt

COPY ./models /server/models
COPY ./Y_blog /server/Y_blog
COPY config.py /server/
COPY main.py /server/
COPY .env /server/
COPY ./media /server/media

WORKDIR /server

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
