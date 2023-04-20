This is a personal project to learn Google Cloud while also moderating elements of a few discords.
The primary feature of this application is to serve a discord role bot, aka federate granting roles to users on specific actions.
Currently the bot watches for emotes on a specific message. Upon seeing an emote from a user it assigns a user that specified role.

TECHNOLOGIES USED:
Python
Docker
Github Actions
Google Cloud Artifact Registry
Google Cloud Compute Engine
Firebase Firestore


The following are links/tutorials that help me run/set up the bot.

VM Setup:
sudo apt-get update #updates the vm
sudo apt-get install python-pip #installs pip
sudo pip install virtualenv #installs virtualenv
virtualenv venv #creates virtual env
source venv/bin/activate #activates virtual env
pip install -r requirements.txt #install packages


Helpful Videos:
#https://www.youtube.com/watch?v=RfJUm-LKNBw
#https://torbjornzetterlund.com/using-secret-manager-in-a-google-cloud-function-with-python/



Running Docker Locally:

run the build file
docker build --build-arg local_build=true -t python-role-bot-dev .

run it locally
docker run -p 5000:5000 python-role-bot-dev:latest

if you get "port is busy" you need to disable airplay in mac settings



Running Docker on VM: 
get the name of the image
docker images

then copy that url and run it
docker run -e env=dev us-central1-docker.pkg.dev/discord-role-bot-380821/discord-role-bot/discord-role-bot-dev:latest
-e is environment variable


How Can I access Google Cloud From My Local Machine?:
first download and install cli
-https://cloud.google.com/sdk/docs/install
say yes to adding to path

once installed, run in terminal
gcloud auth login
gcloud config set project discord-role-bot-380821

Now we need to set up default credential, or adc
https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to

Create a credential file:
gcloud auth application-default login
This will make the default credential your personal login. Need to make it use the service account instead.
located in .config/


Now that I have Google Cloud CLI, how do I make it work in my Docker container locally?:
IT IS UNCLEAR AT THIS TIME IF THIS DID ANYTHING
in terminal, run:
gcloud components install docker-credential-gcr
restart terminal
docker-credential-gcr configure-docker

How I actually got it to work:
Create a service account in google (or reuse the one created via discord bot). Create a credential.json file from that service account and download it to your machine. Put this cred.json in .gitignore and in the app/ folder.
add -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" when you run docker
ex: docker run -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -p 5000:5000 python-role-bot-dev:latest


Environment Variables:
you can set environment variables locally with:
env=dev python main.py
^ make sure you're running in a python terminal not bash

when you run your container, you can set them there too:
docker run -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -e env=dev -p 5000:5000 python-role-bot-dev:latest