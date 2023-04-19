# discord-role-bot
Creating a bot that watches for emotes on a message. upon seeing an emote from a user it assigns a user that specified role.


VM Setup:
sudo apt-get update #updates the vm
sudo apt-get install python-pip #installs pip
sudo pip install virtualenv #installs virtualenv
virtualenv venv #creates virtual env
source venv/bin/activate #activates virtual env
pip install -r requirements.txt #install packages


Running the Bot:
* Run script in no-hangup
nohup python3 -u main.py &[two angle brackets] activity.log &

To stop the bot
* Find all process
ps -ef

* Get PID and kill the task
kill [PID]



Helpful Videos:
#https://www.youtube.com/watch?v=RfJUm-LKNBw
#https://torbjornzetterlund.com/using-secret-manager-in-a-google-cloud-function-with-python/




Docker on google cloud:
https://stackoverflow.com/questions/20429284/how-do-i-run-docker-on-google-compute-engine
sounds like i need to updload to google container instance

and can update through console?
https://stackoverflow.com/questions/62103365/how-to-deploy-container-to-gce-by-updating-container-image




How to run docker locally? and test app?

run the build file
docker build --build-arg local_build=true -t python-role-bot-dev .

run it locally
docker run -p 5000:5000 python-role-bot-dev:latest

if you get "port is busy" you need to disable airplay in mac settings



How to run docker on VM? 
get the name of the image
docker images

then copy that url and run it
docker run us-central1-docker.pkg.dev/discord-role-bot-380821/discord-role-bot/discord-role-bot-dev




google cloud login:
first download and install cli
-https://cloud.google.com/sdk/docs/install
say yes to adding to path

once installed, run in terminal
gcloud auth login
gcloud config set project discord-role-bot-380821


now need to set up default credential, or adc
https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to

create a credential file:
gcloud auth application-default login


getting it to work with docker:
IT IS UNCLEAR AT THIS TIME IF THIS DID ANYTHING
in terminal, run:
gcloud components install docker-credential-gcr
restart terminal
docker-credential-gcr configure-docker

how I actually got it to work:
add the credential.json to the folder thats deployed with docker
add -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" when you run docker
ex: docker run -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -p 5000:5000 python-role-bot-dev:latest



Environment Variables:
you can set environment variables locally with:
env=dev python main.py
^ make sure you're running in a python terminal not bash

when you run your container, you can set them there too:
docker run -e GOOGLE_APPLICATION_CREDENTIALS="svc-acct-cred.json" -e env=dev -p 5000:5000 python-role-bot-dev:latest