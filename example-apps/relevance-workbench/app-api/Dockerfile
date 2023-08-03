FROM python:3.9-slim

RUN apt-get update && rm -rf /var/lib/apt/lists/*

WORKDIR /app-api
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000" ]