FROM python:3.9
RUN apt-get update && apt-get -y install cmake

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]