FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY start_services.sh /app/

RUN chmod +x /app/start_services.sh

CMD ["/app/start_services.sh"]