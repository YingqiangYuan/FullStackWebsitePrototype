FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py /app/app.py
ENV PORT=5003
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5003", "app:app"]
