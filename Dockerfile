# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for the bot token (to be set in Render's environment)
ENV BOT_TOKEN=""

# Expose the port Render will use
EXPOSE $PORT

# Run the bot when the container launches
gunicorn app:app & python3 main.py
