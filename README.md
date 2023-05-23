# Overview
This is a personal project to learn Google Cloud while also moderating elements of a few personal discord communities.
The primary feature of this application is to serve a discord role bot, aka federate granting roles to users on specific actions.
Currently the bot watches for emotes on a specific message. Upon seeing an emote from a user it assigns a user that specified role.

# Technologies Used:
- Python
- Docker
- Github Actions
- Google Cloud Artifact Registry
- Google Cloud Compute Engine
- Firebase Firestore

# Using the Bot:
## Running the Container Locally:

1. Run the build file
`docker build --build-arg local_build=true -t python-role-bot-dev .`

2. Run the built container locally
`docker run -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -e env=dev -p 5000:5000 python-role-bot-dev:latest`

Tip: If you get "port is busy" you need to disable airplay in mac settings. It uses the same port as docker.



## Running Docker on VM: 
1). Get the name of the image
`docker images`

2). Then copy that image name and run it
`docker run -e env=dev -e debug=true us-central1-docker.pkg.dev/discord-role-bot-380821/discord-role-bot/discord-role-bot-dev:latest`
- -e sets an environment variable


## Setting Up Google Cloud CLI on Local Machine:
### Doing this will allow you to access GCP services on your local machine.
1). First download and install [the CLI](https://cloud.google.com/sdk/docs/install)
- Say yes to adding to path. Allows you to reference the CLI from terminal

2). Once installed, run in terminal:
```
gcloud auth login
gcloud config set project discord-role-bot-380821
```

3). Now we need to set up default credential, or [ADC](https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to)
```gcloud auth application-default login```
- This will make the default credential your personal login


## Now that I have Google Cloud CLI, how do I make it work in my Docker container locally?:
### IT IS UNCLEAR AT THIS TIME IF THIS DID ANYTHING
1). In terminal, run:
`gcloud components install docker-credential-gcr`

2). Restart terminal, then run:
`docker-credential-gcr configure-docker`

### How I actually got it to work:
1). Create a service account in google. From there, create a credential.json file from that service account and download it to your machine. Put this cred.json in .gitignore and in the app/ folder.
```
add -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" when you run docker
ex: docker run -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -p 5000:5000 python-role-bot-dev:latest
```

### Environment Variables:
- You can set environment variables locally with:
`env=dev debug=true python main.py`
  - Make sure you're running in a python terminal not bash

- When you run your container, you can set them there too:
`docker run -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -e env=dev -p 5000:5000 python-role-bot-dev:latest`


## Tutorials:
The following are links/tutorials that help me run/set up the bot.

### Helpful Videos:
- [Hosting python on GCP Compute Engine](https://www.youtube.com/watch?v=RfJUm-LKNBw)
- [Getting a secret via Python](https://torbjornzetterlund.com/using-secret-manager-in-a-google-cloud-function-with-python/)
