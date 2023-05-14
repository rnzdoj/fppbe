# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y libpq-dev gcc && pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for database connection
ENV DATABASE_HOST "arjuna.db.elephantsql.com"
ENV DATABASE_NAME "yqfvqfie"
ENV DATABASE_USER "yqfvqfie"
ENV DATABASE_PASSWORD "FOPYHfFC3pRVH7gWg4sC1eCX7Xgnp-lq"

# Run app.py when the container launches
CMD ["python", "main.py"]
