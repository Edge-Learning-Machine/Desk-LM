FROM python:3.6

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8303

CMD ["python3", "api/api.py"]