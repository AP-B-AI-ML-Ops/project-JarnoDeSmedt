FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y git && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Default command (adjust as needed)
CMD ["python", "train_and_register_model.py"]
