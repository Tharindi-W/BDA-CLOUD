# Dockerfile for RedshiftAnalytics Microservice
FROM python:3.10-slim

WORKDIR /app

# Copy requirements file and install dependencies
COPY src/requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y curl

# Copy application source code
COPY src/ .

# Expose the application port
EXPOSE 5005

# Start the application
CMD ["python", "app.py"]
