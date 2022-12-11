from Google import Create_Service
from googleapiclient.errors import HttpError
from datetime import datetime
from pytz import timezone
import pytz
import re

class Gmail_App:
    def __init__(self, first, last, email, label_name):
        self.first = first
        self.last = last
        self.email = email
        self.service = self.create_Google_service()
        self.label_id = self.check_label(label_name)

    def create_Google_service(self):
        CLIENT_SECRET_FILE = 'credentials.json'
        API_NAME = 'gmail'
        API_VERSION = 'v1'
        SCOPES = ['https://mail.google.com/']
        return Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    def test(self):
        labels= self.service.users().labels().list(userId=self.email).execute()
        print(labels)

    def audit_log(self, type, string):
        date_format='%m/%d/%Y %H:%M:%S %Z'
        date = datetime.now(tz=pytz.utc)
        date = date.astimezone(timezone('US/Pacific'))
        fd = open("logfile.txt", 'a')
        fd.writelines(f'{date.strftime(date_format)} | {type} | {string}\n')
        fd.close()
            
            
    def add_quarantine(self, message_ids):
        try:
            body={
                "addLabelIds": [self.label_id],
                "ids": message_ids,
                "removeLabelIds": ['INBOX']
            }
            self.service.users().messages().batchModify(userId=self.email, body=body).execute()
        except HttpError as error:
            print(f'An error occurred: {error}')        # SELF NOTE WRITE TO LOGGING


    def check_label(self, name):
        try:
            labels= self.service.users().labels().list(userId=self.email).execute()
            for label in labels.get("labels"):
                if label.get("name") == name:
                    return label.get("id")
            else: 
                label = self.service.users().labels().create(userId=self.email,body={"name":name}).execute()
                return label.get("id")
        except HttpError as error:
            print(f'An error occurred: {error}')        # SELF NOTE WRITE TO LOGGING

def handler(app):
    try:
        black_lists = open('blacklist.txt', 'r')
        bcontent = black_lists.read()
        emails = app.service.users().messages().list(userId=app.email, labelIds='INBOX').execute()
        blacklist_ids = []
        for messages in emails['messages']:
            m = app.service.users().messages().get(userId=app.email, id=messages.get('id'), format='metadata').execute()
            headers = (m.get("payload")).get("headers")
            subject = next((header.get("value") for header in headers if header["name"] == "Subject"), None)
            sender = next((header.get("value") for header in headers if header["name"] == "From"), None)
            sender_email = re.search('<(.*)>', sender)
            if sender_email.group(1)==bcontent.strip():
                blacklist_ids.append(messages.get('id'))
                app.audit_log("Filter", f'{sender} : {subject}')
            # else:
            #     implicit deny
            #     print("placeholder")
                

        if blacklist_ids:
            app.add_quarantine(blacklist_ids)

    except HttpError as error:
        print(f'An error occurred: {error}')        # SELF NOTE WRITE TO LOGGING

app = Gmail_App("Test", "Account", "spamfilterbottester@gmail.com", "Quarantine")
handler(app)

