# Use a base image with Python 3.12
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the local code to the container
COPY data /app/data

# Install system dependencies for numpy
RUN apt-get update && \
    apt-get install -y \
    git && \
    git clone https://github.com/JaajoJ/telegram-leet-bot.git 
#    liblapack-dev \
#    gfortran \
#    libffi-dev python3 python3-dev gcc libffi-dev

RUN mv telegram-leet-bot/* /app/

ENV TZ=Europe/Helsinki 
# Install any dependencies your script might have
RUN pip install --no-cache-dir -r requirements.txt

# Define a volume for persistent data
VOLUME /app/data

# Command to run your script
CMD ["python", "main.py"]

