FROM python:3.12

# Create app directory
WORKDIR /app

ENV AWS_DEFAULT_REGION=eu-west-1

# Install app dependencies
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY . /app

EXPOSE 8080