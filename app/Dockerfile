# pull official base image
FROM python:3.11.12-slim-bookworm

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN echo "Updating apt-get"
RUN apt-get update

# install GTK3
RUN echo "Installing GTK3 binaries"
RUN apt-get -qq -y install libgtk-3-0

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .