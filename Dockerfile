FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY base_conhecimento/ ./base_conhecimento/

EXPOSE 80

CMD ["streamlit", "run", "main.py", "--server.port=80", "--server.address=0.0.0.0"]