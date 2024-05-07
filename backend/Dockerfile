# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ARG AZURE_OPENAI_API_KEY
ARG OPENAI_API_VERSION
ARG AZURE_OPENAI_ENDPOINT
ARG OPENAI_API_TYPE
ARG OPENAI_DEPLOYMENT_NAME
ARG OPENAI_MODEL_NAME

ENV AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY
ENV OPENAI_API_VERSION=$OPENAI_API_VERSION
ENV AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT
ENV OPENAI_API_TYPE=$OPENAI_API_TYPE
ENV OPENAI_DEPLOYMENT_NAME=$OPENAI_DEPLOYMENT_NAME
ENV OPENAI_MODEL_NAME=$OPENAI_MODEL_NAME

EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]