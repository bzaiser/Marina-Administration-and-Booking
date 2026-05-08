FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install minimal extra dependencies
RUN apt-get update && apt-get install -y \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "marina_project.wsgi:application"]
