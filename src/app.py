from Google import Create_Service

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

emails = service.users().messages().list(userId="spamfilterbottester@gmail.com").execute()

for messages in emails['messages']:
    m = service.users().messages().get(userId="spamfilterbottester@gmail.com", id=messages['id'], format='metadata').execute()
    print(m)
    break

s = service.users().messages().send(userId="spamfilterbottester@gmail.com")