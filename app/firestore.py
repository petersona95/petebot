import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import logger

env = os.getenv('env') # for logging

# Always use the application default credentials
# Default creds are inhereted on VM
# Uses the credential.json on local docker

# Assign credential
cred = credentials.ApplicationDefault()

# log into Firestore
app = firebase_admin.initialize_app(cred)
db = firestore.client()


def get_messageID(guildID):
    '''
    Look up document based on GuildID. Return the messageID saved for that server.
    '''
    doc_ref = db.collection(u'servers').document(str(guildID))
    doc = doc_ref.get()

    if doc.exists:
        doc_json = doc.to_dict()
        messageID = doc_json['messageID']
        return int(messageID) # its a string in firestore, convert to int to match payload
    else:
        logger.write_log(
            action=None,
            payload=f"No messageID exists for guildID: {guildID}. No action was taken.",
            severity='Warning'
        )


def get_role(guildID, payloadEmote):
    '''
    Return a role when given an emote
    '''
    doc_ref = db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote)
    doc = doc_ref.get()

    if doc.exists:
        doc_json = doc.to_dict()
        roleName = doc_json['roleName']
        return roleName
    else:
        logger.write_log(
            action=None,
            payload=f"No document exists for {payloadEmote}, taking no action.",
            severity='Info'
        )
        return None

def add_role(guildID, payloadEmote, roleName):
    '''
    if role collection doesn't exist, it will be created
    if a document for the emote already exists, it will be overwritten
    '''
    # check if the emote already exists
    doc_ref = db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote)
    doc = doc_ref.get()
    exists = False

    if doc.exists:
        doc_json = doc.to_dict()
        oldRoleName = doc_json['roleName']
        logger.write_log(
            action=None,
            payload=f"A role has already ben created for #{oldRoleName} using emote {payloadEmote}.",
            severity='Debug'
        )
        exists = True

    # add an emote:roleName to roles collection
    data = {
        u'roleName': roleName,
        u'roleEmote': payloadEmote
    }
    # add the document
    db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote).set(data)
    user_response = ''

    if exists == True:
        user_response = f'Updated the rule for emote {payloadEmote}. The role has been changed from #{oldRoleName} to #{roleName}'
    else:
        user_response = f'A new rule has been created for the emote {payloadEmote} and role #{roleName}'

    logger.write_log(
        action=None,
        payload=user_response,
        severity='Info'
    )
    return user_response


def remove_role(guildID, payloadEmote):
    '''
    Check if an emote/role name pair exists
    If it does not exist, notify the user
    If it exists, remove it
    '''

    # check if the emote already exists
    doc_ref = db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote)
    doc = doc_ref.get()
    exists = False
    user_response = ''
    if doc.exists:
        doc_json = doc.to_dict()
        RoleName = doc_json['roleName']
        # delete an emote:roleName to roles collection
        db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote).delete()
        user_response = f'Removed rule for the emote {payloadEmote} and role #{RoleName}.'
        logger.write_log(
            action=None,
            payload=user_response,
            severity='Info'
        )
    elif exists == False:
        user_response = f'No role found for emote {payloadEmote}. Taking no action.'
        logger.write_log(
            action=None,
            payload=user_response,
            severity='Debug'
        )
    return user_response


def show_roles(guildID):
    '''
    Return a list of roles to a user
    '''
    # stream used to retrieve multiple docs
    docs = db.collection(u'servers').document(str(guildID)).collection(u'roles').stream()
    doc_list = []
    for doc in docs:
        doc_list.append(doc.to_dict())
    return doc_list