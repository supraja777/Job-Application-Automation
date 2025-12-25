from authenticate_gmail import authenticate_gmail
from utility import fetch_unread_emails, get_email_details
from llm import determine_action_needed

if __name__ == '__main__':
    service = authenticate_gmail()
    messages = fetch_unread_emails(service, max_results=5)

    if not messages:
        print("No unread emails.")
    else:
        for msg in messages:
            email_details = get_email_details(service, msg['id'])
            determine_action_needed(email_details, service)