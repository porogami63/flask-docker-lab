FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Copy static files
COPY public ./public

ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV PORT=10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app.main:app"]
