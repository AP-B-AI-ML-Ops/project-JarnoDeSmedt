FROM prefecthq/prefect:3.4.2-python3.12-conda

# Set the working directory
WORKDIR /app

# Copy requirements.txt from project root into the image
COPY requirements.txt .

# Install all dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
