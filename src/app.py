from Gmail_App import Gmail_App
from googleapiclient.errors import HttpError
import re

def handler(app):
    try:
        black_lists = open('blacklist.txt', 'r')
        bcontent = black_lists.read()
        print("here")
        service = app.create_Google_service()
        emails = service.users().messages().list(userId=app.email, labelIds='INBOX').execute()
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
        print(f'An error occurred: {error}')        # app NOTE WRITE TO LOGGING
            

app = Gmail_App("Test", "Account", "spamfilterbottester@gmail.com", "Quarantine")
handler(app)

