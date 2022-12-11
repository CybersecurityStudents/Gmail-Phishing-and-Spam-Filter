from Google import Create_Service
from googleapiclient.errors import HttpError

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
    
    def list_inbox(self):
        try:
            return self.service.users().messages().list(userId=self.email, labelIds='INBOX').execute()
        except HttpError as error:
            print(f'An error occurred: {error}')        # SELF NOTE WRITE TO LOGGING
            return False
    
    def get_message(self, message_id):
        try:
            return self.service.users().messages().get(userId=self.email, id=message_id, format='metadata').execute()
        except HttpError as error:
            print(f'An error occurred: {error}')        # SELF NOTE WRITE TO LOGGING
            return False

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