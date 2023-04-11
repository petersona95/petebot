# Dockerfile - blueprint for building images
# gives you docker image that has all the python stuff
FROM python:3.8 

# adds the python script. the . is the main directory
# ADD main.py .
# ADD get_secret.py .
# ADD requirements.txt .
# ADD config.json .
# if on local machine it will add, if on gcp it will add nothing but an empty folder
# prevents failure because no files are found. also prevents uploading sensitive token
# local files are not saved to git
ADD app/ .

# install dependencies
RUN pip install -r requirements.txt

# run main.py in our container terminal
CMD ["python", "./main.py"]

# Image - template for running containers
## run in cmd line
# docker build -t python-role-bot [press enter]
## specify location
# . [press enter]


# Container - Packaged project
## start container
# docker run python-role-bot