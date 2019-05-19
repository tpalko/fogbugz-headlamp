FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev libpq-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD [ "python", "run.py", "runserver" ]
