from firebase_stuff import readJson, DatetimeWithNanoseconds, credentials, firebase_admin, firestore, setDocument, getDocument, getCollectionDocs, writeJson
import pytz
import datetime
import os
from dotenv import load_dotenv, dotenv_values

def getPastEvents(store):
    """
    get all the events from the Events collection in Firestore
    """
    documents = getCollectionDocs(store, "Events")
    for data in documents:
        for field in data:
            data[field] = str(data[field])
    writeJson(r"firestore-events.json", documents)
    # print(len(documents))

def getDocumentsAndSave(store, collectionName, jsonPath):
    """
    get all the documents from a Firestore collection and save to a json file locally
    """
    documents = getCollectionDocs(store, collectionName)
    writeJson(jsonPath, documents)
    # print(len(documents))

def getDocumentsAndSetAnother(store, oldCollectionName, newCollectionName, newDocName):
    """
    get all the documents in a Firestore collection and create/update document
    """
    documents = getCollectionDocs(store, oldCollectionName)
    setDocument(store, newCollectionName, newDocName, {oldCollectionName: documents})

def compareAndUpdate(store, collectionName, documentName):
    """
    compare the events in the file with the newly scraped events and update accordingly
    """
    data = readJson("events.json")
    convertDate(data)
    document = getDocument(store, collectionName, documentName)
    
    for datum in document["Scraped Events"]:
        if datum in data["Scraped Events"]:
            if document["Scraped Events"][datum] == data["Scraped Events"][datum]:
                continue
            document["Scraped Events"][datum] = data["Scraped Events"][datum]
        else:
            del document["Scraped Events"][datum]
    
    for datum in data["Scraped Events"]:
        if datum in document["Scraped Events"]:
            if document["Scraped Events"][datum] == data["Scraped Events"][datum]:
                continue
            else:
                document["Scraped Events"][datum] = data["Scraped Events"][datum]
        else:
            document["Scraped Events"][datum] = data["Scraped Events"][datum]

    setDocument(store, collectionName, documentName, document)

def convertDate(data):
    for datum in data["Scraped Events"]:
        raw_date = data["Scraped Events"][datum]["Date"]
        data["Scraped Events"][datum]["Date"] = DatetimeWithNanoseconds(raw_date[0], raw_date[1], raw_date[2], (raw_date[3]+6) % 24, raw_date[4], raw_date[5], 0)
    
if "__main__" == __name__:

    load_dotenv(r"blugh/.env")
    file_name = os.getenv("CREDENTIALS_PATH")
    cred = credentials.Certificate(file_name)
    firebase_admin.initialize_app(cred)
    store = firestore.client()