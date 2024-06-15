FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install -r requirements.txt

COPY . .

RUN mkdir -p logs

EXPOSE 5000

CMD ["python", "run.py"]
