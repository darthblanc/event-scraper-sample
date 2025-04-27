import firebase_admin
import google.cloud
from firebase_admin import firestore, credentials
import google.cloud.exceptions
import json
from google.api_core.datetime_helpers import DatetimeWithNanoseconds

def getDocumentRef(client, collection_name: str, doc_name: str):
    return client.collection(collection_name).document(doc_name)

def getDocumentSnapshot(document):
    return document.get()

def convertSnapshotToDict(snapshot) -> dict:
    return snapshot.to_dict()

def getDocument(client, collection_name, doc_name):
    document = getDocumentRef(client, collection_name, doc_name)
    snapshot =  getDocumentSnapshot(document)
    return convertSnapshotToDict(snapshot)

def getCollectionDocs(client, collection_name: str):
    collection_ref = client.collection(collection_name)
    docs = collection_ref.stream()
    return [convertSnapshotToDict(doc) for doc in docs]

def setDocument(client, collection_name: str, doc_name: str, data) -> None:
    doc_ref = getDocumentRef(client, collection_name, doc_name)
    doc_ref.set(data)
    return

def createCollection(client, collection_name: str):
    return client.collection(collection_name)

def createDocument(client, collection_name: str, doc_name: str):
    return client.collection(collection_name).document(doc_name)

def readJson(path: str):
    fd = open(path, "r")
    data = json.load(fd)
    fd.close()
    return data

def writeJson(path: str, data):
    with open(path, 'w') as fd:
        fd.write(json.dumps(data, indent=4))
    return