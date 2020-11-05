FROM python:3.6

WORKDIR /app

COPY /requirements.txt /app

RUN pip3 install -r requirements.txt

COPY config/ /app
COPY output/ /app
COPY api/ /app
COPY utils/ /app
COPY output/ /app

COPY error.py /app
COPY logger.py /app
COPY main.py /app
COPY README.md /app

CMD ["python3", "api.py"]