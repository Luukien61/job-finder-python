FROM python:3.9.20
WORKDIR /app
COPY *.py .
COPY .env .
COPY requirement.txt .
RUN pip install -r requirement.txt
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
LABEL authors="luukien"
EXPOSE 8000
CMD ["python", "main.py"]