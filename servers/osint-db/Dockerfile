FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

ENV OSINT_DB_PATH=/data/osint.db \
    HOST=0.0.0.0 \
    PORT=8765

EXPOSE 8765

CMD ["python", "server.py"]
