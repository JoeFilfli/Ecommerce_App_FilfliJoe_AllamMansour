# Start with an official Python image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Expose port 5000
EXPOSE 5000

ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0"]

