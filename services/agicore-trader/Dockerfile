# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application using a production-grade server
# The --host 0.0.0.0 flag is crucial for Cloud Run to receive requests
CMD ["sh","-c","PORT=${PORT:-8080}; exec uvicorn main:app --host 0.0.0.0 --port $PORT"]
