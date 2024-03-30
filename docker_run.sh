#!/bin/bash

container_name="python-role-bot-dev"

# Stop the container
docker stop $container_name || true

# Remove the container
docker rm $container_name || true

# Build the Docker image
docker build --build-arg local_build=true -t python-role-bot-dev .

# Run a new container
docker run --name $container_name -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -e env=dev -e debug=true -p 5000:5000 python-role-bot-dev:latest