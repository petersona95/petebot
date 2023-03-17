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