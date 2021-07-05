FROM python:3.9.6-slim

WORKDIR /

COPY src /

ENTRYPOINT ["python3", "/mailsender.py"]
