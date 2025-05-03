# Use an official Python runtime as a parent image
FROM python:3.12.5

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY src/requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY src/ /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD gunicorn calendar_converter.wsgi:application --bind 0.0.0.0:$PORT --log-file -