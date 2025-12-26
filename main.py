from authenticate_gmail import authenticate_gmail
from utility import fetch_unread_emails, get_email_details, mark_as_read
from llm import is_action_needed, is_application_acknowledgment

if __name__ == '__main__':
    service = authenticate_gmail()
    messages = fetch_unread_emails(service, max_results=25)
    if not messages:
        print("No unread emails.")
    else:
        number_of_jobs_applied = 0
        email_cnt = 0
        for msg in messages:
       
            email_cnt += 1
            email_details = get_email_details(service, msg['id'])
            message_id = email_details['id']

            mark_as_read(service, message_id)
            # is_action_needed(email_details, service)
            number_of_jobs_applied += is_application_acknowledgment(email_details, service)

        print("Number of jobs applied ",number_of_jobs_applied)
        print("Number of messages processed ", email_cnt)

