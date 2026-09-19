# Use official Python base image
FROM python:3.11-slim
# Set working directory inside container
WORKDIR /app
# Copy dependency file first
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy application
COPY . .
# Expose Flask port
EXPOSE 5000
# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
# Run application
CMD ["python", "app.py"]
