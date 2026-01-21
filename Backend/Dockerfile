# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "backapi.wsgi:application", "--bind", "0.0.0.0:8000"]
