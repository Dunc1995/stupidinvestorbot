
FROM python:3.12

# Create app directory
WORKDIR /marketsimulator

# Install app dependencies
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY . /marketsimulator

EXPOSE 8081