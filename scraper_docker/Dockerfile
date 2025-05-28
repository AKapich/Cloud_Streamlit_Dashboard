FROM python:3.12-slim

WORKDIR /scraper

COPY final_scraper.py .
COPY requirements.txt .
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "final_scraper.py"]

