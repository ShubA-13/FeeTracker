# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster
WORKDIR /main
COPY * ./
RUN pip install -r /main/requirements.txt
EXPOSE 5000/tcp
CMD [ "python3", "/main/main.py"]