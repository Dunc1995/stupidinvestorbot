
FROM python:3.12

ARG CRYPTO_KEY
ARG CRYPTO_SECRET_KEY

# Create app directory
WORKDIR /investorbot

ENV AWS_DEFAULT_REGION=eu-west-1

# Install app dependencies
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY . /investorbot

EXPOSE 8080