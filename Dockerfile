FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/service-account.json

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
