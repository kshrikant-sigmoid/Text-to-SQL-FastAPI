FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend.py .
COPY Chinook.db .
EXPOSE 80
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "80"]

