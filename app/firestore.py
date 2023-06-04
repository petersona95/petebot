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

def set_messageID(guildID, messageID, channelID):
    '''
    Set the value for a messageID in firestore. Will also create the feature for roleSelect in a channel
    '''
    # otherwise add user to collection
    data = {
        u'enabled': 'true',
        u'messageID': messageID,
        u'channelID': channelID
    }
    # add the document
    db.collection(u'servers').document(str(guildID)).collection(u'features').document(u'roleSelect').set(data)


def get_messageID(guildID):
    '''
    Look up document based on GuildID. Return the messageID saved for that server.
    '''
    doc_ref = db.collection(u'servers').document(str(guildID)).collection(u'features').document('roleSelect')
    doc = doc_ref.get()

    if doc.exists:
        doc_json = doc.to_dict()
        response = {
            'messageID' : int(doc_json['messageID']),
            'channelID' : int(doc_json['channelID'])
        }
        return response # its a string in firestore, convert to int to match payload}
    else:
        logger.write_log(
            action=None,
            payload=f"The roleSelect feature was not found. No action was taken.",
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
    doc_ref = db.collection(u'servers').document(str(guildID)).collection(u'features').document('roleSelect').collection(u'roles').document(payloadEmote)
    doc = doc_ref.get()
    exists = False

    if doc.exists:
        doc_json = doc.to_dict()
        oldRoleName = doc_json['roleName']
        logger.write_log(
            action=None,
            payload=f"A role has already been created for #{oldRoleName} using emote {payloadEmote}.",
            severity='Debug'
        )
        exists = True

    # add an emote:roleName to roles collection
    data = {
        u'roleName': roleName,
        u'roleEmote': payloadEmote
    }
    # add the document
    db.collection(u'servers').document(str(guildID)).collection(u'features').document('roleSelect').collection(u'roles').document(payloadEmote).set(data)
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


class travianUser():
    def __init__(self, userId, discordUsername, travianUsername, allianceRole, guildId):
        self.userId = userId
        self.discordUsername = discordUsername
        self.travianUsername = travianUsername
        self.allianceRole = allianceRole
        self.guildId = guildId

    def add_user(self):
        '''
        add a document for the specified Travian user
        '''
        # query if rejected user
        docs = db.collection(u'servers').document(str(self.guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').where('userId', '==', str(self.userId)).where('rejected', '==', 'true').stream()
        doc_list = []
        for doc in docs: # will return 0 or one row
            doc_list.append(doc.to_dict())
            if doc_list: # check if any records returned
                return 'Rejected' # user has been rejected

        # query if user is already approved
        docs = db.collection(u'servers').document(str(self.guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').where('userId', '==', str(self.userId)).where('approved', '==', 'true').stream()
        doc_list = []
        for doc in docs: # will return 0 or one row
            doc_list.append(doc.to_dict())
            if doc_list: # check if any records returned
                return 'Approved' # user has been approved to another alliance
            
        # # query if username already exists and it's not from the existing user
        docs = db.collection(u'servers').document(str(self.guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').where('travianUsername', '==', str(self.travianUsername).lower()).where('userId', '!=', str(self.userId)).stream()
        doc_list = []
        for doc in docs: # will return 0 or one row
            doc_list.append(doc.to_dict())
            if doc_list: # check if any records returned

                # otherwise add user to collection
                data = {
                    u'userId': str(self.userId),
                    u'discordUsername': self.discordUsername,
                    u'travianUsername': f'{self.travianUsername} - REJECTED: DUPLICATE',
                    u'allianceRole': self.allianceRole,
                    u'approved': 'false',
                    u'rejected': 'true'
                }
                # add the document
                db.collection(u'servers').document(str(self.guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').document(str(self.userId)).set(data)
                return 'Duplicate UN' # User chose a UN that someone else already registered. rejected.

        # otherwise add user to collection
        data = {
            u'userId': str(self.userId),
            u'discordUsername': self.discordUsername,
            u'travianUsername': self.travianUsername,
            u'allianceRole': self.allianceRole,
            u'approved': 'false',
            u'rejected': 'false'
        }
        # add the document
        db.collection(u'servers').document(str(self.guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').document(str(self.userId)).set(data)
        return 'Success'

def get_pending_users(guildId, allianceRole):
    '''
    Get details of all users. returns many
    '''
    docs = db.collection(u'servers').document(str(guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').where('allianceRole', '==', allianceRole).where('approved', '==', 'false').where('rejected', '==', 'false').stream()
    doc_list = []
    for doc in docs: # will return one row
        doc_list.append(doc.to_dict())
    return doc_list

def check_user(guildId, travianUsername):
    '''
    Get details of a user. returns 1 user
    '''
    # get users where travianUsername = travianUsername & approved = false
    docs = db.collection(u'servers').document(str(guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').where('travianUsername', '==', travianUsername).where('approved', '==', 'false').where('rejected', '==', 'false').stream()
    doc_list = []
    for doc in docs: # will return one row
        doc_list.append(doc.to_dict())
        if doc_list: # check if any records returned
            for user in doc_list: # will iterate over one dictionary entry
                return user


def approve_user(guildId, travianUsername):
    '''
    Update user to be approved
    '''
    # get users where travianUsername = travianUsername & approved = false
    docs = db.collection(u'servers').document(str(guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').where('travianUsername', '==', travianUsername).where('approved', '==', 'false').where('rejected', '==', 'false').stream()
    doc_list = []
    for doc in docs: # will return one row
        doc_list.append(doc.to_dict())
        if doc_list: # check if any records returned
            for user in doc_list: # will iterate over one dictionary entry
                #for i in dict:
                db.collection(u'servers').document(str(guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').document(str(user["userId"])).update({
                    'approved': 'true'
                })
                return user

def approve_all_users(guildId, allianceRole):
    '''
    Update user to be approved
    '''
    # get users where travianUsername = travianUsername & approved = false
    docs = db.collection(u'servers').document(str(guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').where('allianceRole', '==', allianceRole).where('approved', '==', 'false').where('rejected', '==', 'false').stream()
    doc_list = []
    for doc in docs: # can return many rows
        doc_list.append(doc.to_dict())
        if doc_list: # check if any records returned
            for user in doc_list: # will iterate over every dictionary entry
                #for i in dict:
                db.collection(u'servers').document(str(guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').document(str(user["userId"])).update({
                    'approved': 'true'
                })
    return doc_list

def reject_user(guildId, travianUsername):
    '''
    Update user to be rejected
    '''
    # get users where travianUsername = travianUsername & approved = false
    docs = db.collection(u'servers').document(str(guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').where('travianUsername', '==', travianUsername).where('approved', '==', 'false').stream()
    doc_list = []
    for doc in docs: # will return one row
        doc_list.append(doc.to_dict())
        if doc_list: # check if any records returned
            for user in doc_list: # will iterate over one dictionary entry
                #for i in dict:
                db.collection(u'servers').document(str(guildId)).collection(u'features').document(u'TravianApproval').collection(u'users').document(str(user["userId"])).update({
                    'rejected': 'true'
                })
                return user