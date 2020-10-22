FROM python:3.6

WORKDIR /app

COPY /requirements.txt /app

RUN pip3 install -r requirements.txt

COPY config/ /app
COPY output/ /app
COPY src/ /app
COPY utils/ /app
COPY output/ /app

COPY error.py /app
COPY logger.py /app
COPY main.py /app
COPY README.md /app

CMD ["python3", "api.py"]

#COPY requirements.txt /
#RUN pip3 install -r /requirements.txt

#COPY config/ /app
#COPY datasets/ /app
#COPY input/ /app
#COPY output/ /app
#COPY src/ /app
#COPY utils/ /app
#COPY zip/ /app
#COPY error.py /app
#COPY logger.py /app
#COPY main.py /app
#COPY README.md /app/.
#WORKDIR /app

#EXPOSE 5001

#CMD [ "python3", "server.py" ]