FROM python:3.9-slim

WORKDIR /app

COPY ../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY aggregator.py .

CMD ["python", "aggregator.py"]