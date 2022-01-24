FROM ubuntu:latest
MAINTAINER Sohaib "sohaibayub9@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential python3-sqlalchemy python3-mysqldb
ADD . /myapp
WORKDIR /myapp
RUN pip install -r requirements.txt
ENTRYPOINT python3 run.py