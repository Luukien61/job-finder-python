FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY *.py .
COPY gender-weights/ gender-weights/
COPY requirement.txt .

RUN pip install --no-cache-dir -r requirement.txt

LABEL authors="luukien"
EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
