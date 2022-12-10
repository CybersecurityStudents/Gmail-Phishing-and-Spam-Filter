from Google import Create_Service

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

    def handler(self):
        black_lists = open('blacklist.txt', 'r')
        bcontent = black_lists.read()
        white_lists = open('whitelist.txt', 'r')
        wcontent = white_lists.read()
        emails = self.service.users().messages().list(userId=self.email).execute()
        for messages in emails['messages']:
            m = self.service.users().messages().get(userId=self.email, id=messages.get('id'), format='metadata').execute()
            headers = (m.get("payload")).get("headers")
            for header in headers:
                if header.get("name")=="From":
                    start = "<"
                    end = ">"
                    s = header.get("value")
                    sender = s[s.find(start)+len(start):s.rfind(end)]
                    if sender==bcontent.strip():
                        self.add_quaratine(messages.get('id'))    
                    elif sender==wcontent.strip():
                        print("problem this guy is in our whitelist filter")
                    else:
                        #implicit deny
                        print("placeholder")
    
    def add_quaratine(self, message_id):
        body={
            "addLabelIds": [self.label_id]
        }
        self.service.users().messages().modify(userId=self.email, id=message_id, body=body).execute()

    def check_label(self, name):
        labels= self.service.users().labels().list(userId=self.email).execute()
        for label in labels.get("labels"):
            if label.get("name") == name:
                return label.get("id")
        else:
            label = self.service.users().labels().create(userId=self.email,body={"name":name}).execute()
            return label.get("id")
            

app = Gmail_App("Test", "Account", "spamfilterbottester@gmail.com", "Quarantine")
app.handler()
