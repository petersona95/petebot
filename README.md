# Overview
This is a personal project to learn Google Cloud while also moderating elements of a few personal discord communities.
The primary feature of this application is to serve a discord role bot, aka federate granting roles to users on specific actions.
Currently the bot watches for emotes on a specific message. Upon seeing an emote from a user it assigns a user that specified role.

# Technologies Used:
Python
Docker
Github Actions
Google Cloud Artifact Registry
Google Cloud Compute Engine
Firebase Firestore

# Using the Bot:
### Running the Container Locally:

run the build file
`docker build --build-arg local_build=true -t python-role-bot-dev .`

run it locally
`docker run -p 5000:5000 python-role-bot-dev:latest`

if you get "port is busy" you need to disable airplay in mac settings



### Running Docker on VM: 
get the name of the image
`docker images`

then copy that url and run it
`docker run -e env=dev us-central1-docker.pkg.dev/discord-role-bot-380821/discord-role-bot/discord-role-bot-dev:latest`
-e is environment variable


### Setting Up Google Cloud CLI on Local Machine:
Doing this will allow you to access GCP services on your local machine.
first download and install cli
-https://cloud.google.com/sdk/docs/install
say yes to adding to path

once installed, run in terminal
`gcloud auth login`
`gcloud config set project discord-role-bot-380821`

Now we need to set up default credential, or adc
https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to

Create a credential file:
`gcloud auth application-default login`
This will make the default credential your personal login. Need to make it use the service account instead.
located in .config/


### Now that I have Google Cloud CLI, how do I make it work in my Docker container locally?:
IT IS UNCLEAR AT THIS TIME IF THIS DID ANYTHING
in terminal, run:
`gcloud components install docker-credential-gcr`
restart terminal, then run:
`docker-credential-gcr configure-docker`

### How I actually got it to work:
Create a service account in google (or reuse the one created via discord bot). Create a credential.json file from that service account and download it to your machine. Put this cred.json in .gitignore and in the app/ folder.
`add -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" when you run docker`
`ex: docker run -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -p 5000:5000 python-role-bot-dev:latest`


### Environment Variables:
you can set environment variables locally with:
`env=dev python main.py`
^ make sure you're running in a python terminal not bash

when you run your container, you can set them there too:
`docker run -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -e env=dev -p 5000:5000 python-role-bot-dev:latest`


## Tutorials:
The following are links/tutorials that help me run/set up the bot.

### Helpful Videos:
#https://www.youtube.com/watch?v=RfJUm-LKNBw
#https://torbjornzetterlund.com/using-secret-manager-in-a-google-cloud-function-with-python/
