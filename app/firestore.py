import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
# Default creds are inhereted on VM
# Uses the credential.json on local docker

# Assign credential
cred = credentials.ApplicationDefault()

# log into Firestore
app = firebase_admin.initialize_app(cred)
db = firestore.client()


def get_messageID(guildID):
    # look up document based on documentid, GuildID
    doc_ref = db.collection(u'servers').document(str(guildID))
    doc = doc_ref.get()

    if doc.exists:
        doc_json = doc.to_dict()
        messageID = doc_json['messageID']
        return int(messageID) # its a string in firestore, convert to int to match payload
    else:
        print(u'No such document!')

def get_role(guildID, payloadEmote):
    doc_ref = db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote)
    doc = doc_ref.get()

    if doc.exists:
        doc_json = doc.to_dict()
        roleName = doc_json[payloadEmote]
        return roleName
    else:
        print(u'No such document!')
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
        oldRoleName = doc_json[payloadEmote]
        print(f'I already see a role called {oldRoleName} for emote {payloadEmote}.')
        exists = True

    # add an emote:roleName to roles collection
    data = {
    payloadEmote: roleName
    }
    # add the document
    db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote).set(data)
    if exists == True:
        return f'I have updated the rule for emote {payloadEmote}. I''ve changed the role from {oldRoleName} to {roleName}'
    else:
        return f'I have created a new rule for the emote {payloadEmote} and role {roleName}'


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

    if doc.exists:
        doc_json = doc.to_dict()
        RoleName = doc_json[payloadEmote]
        # delete an emote:roleName to roles collection
        db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote).delete()
        return f'The rule  for the emote {payloadEmote} and role {RoleName} has been successfully deleted!'
        exists = True
    elif exists == False:
        return f'No role found for emote {payloadEmote}. Taking no action.'

    
    return

def show_roles(guildID):
    '''
    Return a list of roles to a user
    '''
    # stream used to retrieve multiple docs
    docs = db.collection(u'servers').document(str(guildID)).collection(u'roles').stream()
    doc_list = []
    for doc in docs:
        # dict = {'id': doc.id , 'document' : doc.to_dict()}
        # doc_list.append(dict)

        doc_list.append(doc.to_dict())
    if not doc_list:
        print('There are no roles currently set for this server.')
    return doc_list



# print(retreive_role(321705601640169472,'🎵'))
#add_role(321705601640169472,'🤣', 'test2')
#remove_role(321705601640169472,'🤣', 'test2')


# add_role(321705601640169472,'🤣', 'test')
# add_role(321705601640169472,'🎵', 'tunes')
# print(show_roles(321705601640169472))
# print(get_role(321705601640169472,'🎵'))