from google.cloud import logging

'''
Writes logs to google cloud logging with varying severity.
Logs are separated by name, all logs will have the same name, discord-role-bot
'''

client = logging.Client()
logger = client.logger('discord-role-bot') # the log name

def create_log(env, payload, severity):
    try:
        logger.log_struct(
            {
                "env": env,
                "message": payload,
                "severity": severity,
            }
        )
    except Exception as e:
        logger.log_struct(
            {
                "env": env,
                "message": 'Failed to write log. Error: ' + str(e),
                "severity": 'HIGH',
            }
        )