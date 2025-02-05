FROM python:3.10-slim

RUN apt-get update && apt-get install -y chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安裝 Python 套件，但不要裝 webdriver-manager
RUN pip install --no-cache-dir selenium requests

RUN pip install --no-cache-dir selenium webdriver-manager requests

COPY . .

CMD ["python", "CheckTicket.py"]
