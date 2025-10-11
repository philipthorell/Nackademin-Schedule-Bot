# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR ./

# Set timezone (for your 6:00 schedule)
ENV TZ=Europe/Stockholm
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Default command to run your bot
CMD ["python", "main.py"]
