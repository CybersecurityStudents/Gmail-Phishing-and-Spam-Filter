import Gmail_App
from datetime import datetime
import pytz
import re

def audit_log(self, type, string):
        date_format='%m/%d/%Y %H:%M:%S %Z'
        date = datetime.now(tz=pytz.utc)
        date = date.astimezone(pytz.timezone('US/Pacific'))
        fd = open("logfile.txt", 'a')
        fd.writelines(f'{date.strftime(date_format)} | {type} | {string}\n')
        fd.close()

def handler(app):
        black_lists = open('blacklist.txt', 'r')
        bcontent = black_lists.read()
        emails = app.list_inbox()
        blacklist_ids = []
        for messages in emails['messages']:
            m = app.get_message(messages.get('id'))
            headers = (m.get("payload")).get("headers")
            subject = next((header.get("value") for header in headers if header["name"] == "Subject"), None)
            sender = next((header.get("value") for header in headers if header["name"] == "From"), None)
            sender_email = re.search('<(.*)>', sender)
            if sender_email.group(1)==bcontent.strip():
                blacklist_ids.append(messages.get('id'))
                audit_log("Filter", f'{sender} : {subject}')
            # else:
            #     implicit deny
            #     print("placeholder")
                

        if blacklist_ids:
            app.add_quarantine(blacklist_ids)

app = Gmail_App("Test", "Account", "spamfilterbottester@gmail.com", "Quarantine")
handler(app)

