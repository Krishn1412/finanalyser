# Use an official Python image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the required files to the container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port (same as what Uvicorn runs on)
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "app.api.api:app", "--host", "0.0.0.0", "--port", "8000"]
