def get_email_details(service, message_id):
    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    headers = message['payload']['headers']
    
    details = {}
    for header in headers:
        if header['name'] == 'From':
            details['from'] = header['value']
        elif header['name'] == 'Subject':
            details['subject'] = header['value']
        elif header['name'] == 'Date':
            details['date'] = header['value']
    
    # Short snippet of email body
    details['snippet'] = message.get('snippet')
    details['id'] = message_id
    return details



def fetch_unread_emails(service, max_results=10):
    # Query: unread emails
    results = service.users().messages().list(
        userId='me', q='is:unread', maxResults=max_results).execute()
    messages = results.get('messages', [])
    return messages


def add_label(service, message_id, label_name):
    # Check if label exists, create if not
    print("Moving to " + label_name + "folder")
    remove_from_inbox(service, message_id)
    labels = service.users().labels().list(userId='me').execute()
    label_id = None
    for label in labels['labels']:
        if label['name'] == label_name:
            label_id = label['id']
            break
    if not label_id:
        label = service.users().labels().create(
            userId='me',
            body={"name": label_name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
        ).execute()
        label_id = label['id']

    # Add label to email
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={"addLabelIds": [label_id]}
    ).execute()


def remove_from_inbox(service, message_id):
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "removeLabelIds": ["INBOX"]
        }
    ).execute()

def mark_as_read(service, message_id):
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "removeLabelIds": ["UNREAD"]
        }
    ).execute()
