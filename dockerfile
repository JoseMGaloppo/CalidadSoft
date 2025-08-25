FROM python:3.11

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]