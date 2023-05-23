from google.cloud import logging as gcp_logging
import logging
from sys import stdout
import os

debug = os.getenv('debug') # only print docker logs if debug=True
env = os.getenv('env')

'''
Writes logs to google cloud logging with varying severity.
Logs are separated by name, all logs will have the same name, discord-role-bot
also writes logs to stdout for local debugging and transparency
severity includes INFO, WARNING, ERROR, etc.
'''

# gcp logging setup
client = gcp_logging.Client()
gcp_logger = client.logger('discord-role-bot') # the log name

# Docker logging setup
logger = logging.getLogger('discord-role-bot')
logger.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stderr
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

def write_log(action, payload, severity):
    try:
        gcp_logger.log_struct(
            {
                "env": env
                ,"action": action
                ,"message": payload
            }
            ,severity=severity
        )

        #write docker log
        if debug.lower()=='true':
            logger.info(payload)

    except Exception as e:
        gcp_logger.log_struct(
            {
                "env": env
                ,"action": action
                ,"message": 'Failed to write log. Error: ' + str(e)
            }
            ,severity=severity
        )

        #write docker log
        if debug.lower()=='true':
            logger.info(payload)