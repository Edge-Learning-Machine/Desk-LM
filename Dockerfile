FROM python:3.6

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY config/ /app
COPY datasets/ /app
COPY input/ /app
COPY output/ /app
COPY src/ /app
COPY utils/ /app
COPY zip/ /app
COPY error.py /app
COPY logger.py /app
COPY main.py /app
COPY README.md /app/.
WORKDIR /app

CMD [ "python", "server.py" ]