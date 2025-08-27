FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY .env .
COPY start.sh .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*


RUN chmod +x start.sh

EXPOSE 5000

CMD ["./start.sh"]