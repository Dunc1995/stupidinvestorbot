FROM python:3.12

# Create app directory
WORKDIR /app

# Install app dependencies
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY . /app

EXPOSE 8080
CMD [ "chalice", "local", "--host", "0.0.0.0", "--port", "8080" ]