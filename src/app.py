from Google import Create_Service
from googleapiclient.errors import HttpError
from datetime import datetime
from pytz import timezone
import pytz

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
        fd = open("audit.txt", 'a')
        fd.writelines(f'{date.strftime(date_format)} {type}: {string}\n')

    def handler(self):
        try:
            black_lists = open('blacklist.txt', 'r')
            bcontent = black_lists.read()
            white_lists = open('whitelist.txt', 'r')
            wcontent = white_lists.read()
            emails = self.service.users().messages().list(userId=self.email, labelIds='INBOX').execute()
            blacklist_ids = []
            
            for messages in emails['messages']:
                m = self.service.users().messages().get(userId=self.email, id=messages.get('id'), format='metadata').execute()
                headers = (m.get("payload")).get("headers")
                for header in headers:
                    subject = None
                    if header.get("name")=="Subject":
                        subject = header.get("value")
                        print(subject)
                    if header.get("name")=="From":
                        start = "<"
                        end = ">"
                        s = header.get("value")
                        sender = s[s.find(start)+len(start):s.rfind(end)]
                        print(sender)
                        if sender==bcontent.strip():
                            blacklist_ids.append(messages.get('id')) 
                            self.audit_log("Filter", f'<{sender}> {subject}')
                        elif sender==wcontent.strip():
                            print("problem this guy is in our whitelist filter")
                        # else:
                        #     #implicit deny
                        #     print("placeholder")
                    
            if blacklist_ids:
                self.add_quarantine(blacklist_ids)

        except HttpError as error:
            print(f'An error occurred: {error}')        # SELF NOTE WRITE TO LOGGING
            
            
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
            

app = Gmail_App("Test", "Account", "spamfilterbottester@gmail.com", "Quarantine")
app.handler()

