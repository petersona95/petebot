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
        messageID = doc_json['messageID'] # its a string in firestore, convert to int
        return int(messageID)
    else:
        print(u'No such document!')

def get_role(guildID, payloadEmote):
    doc_ref = db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote)
    doc = doc_ref.get()

    if doc.exists:
        doc_json = doc.to_dict()
        roleName = doc_json['roleName']
        return roleName
    else:
        print(u'No such document!')

def add_role(guildID, payloadEmote, roleName):
    # check if role collection exists. If it doesn't, create it
    col_ref = db.collection(u'servers').document(str(guildID)).collection(u'roles')
    col = col_ref.get()
    # code is failing at this point - works to create a new document below
    if col.exists:
        print('I see the roles collection')
    else:
        print('No roles collection found. Creating one...')
        db.collection(u'servers').document(str(guildID)).collection(u'roles')

    # add an emote:roleName to roles collection
    data = {
    payloadEmote: roleName
    }

    # add the document
    db.collection(u'servers').document(str(guildID)).collection(u'roles').document(payloadEmote).set(data)


def remove_role():
    return




# sub_doc_ref = db.collection(u'servers').document(u'321705601640169472').collection(u'roles').document(u'🎵')
# sub_doc = sub_doc_ref.get()

# if sub_doc.exists:
#     print(f'Document data: {sub_doc.to_dict()}')
# else:
#     print(u'No such document!')


# print(retreive_role(321705601640169472,'🎵'))
# add_role(321705601640169472,'🤣', 'test')