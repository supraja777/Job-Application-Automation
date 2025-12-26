from authenticate_gmail import authenticate_gmail
from utility import fetch_unread_emails, get_email_details, mark_as_read
from llm import is_action_needed, is_application_acknowledgment, extract_application_information
from update_tracker_sheet import json_to_excel
from utility import remove_from_inbox
from load_data import delete_json_file

if __name__ == '__main__':
    service = authenticate_gmail()
    messages = fetch_unread_emails(service, max_results=13)
    if not messages:
        print("No unread emails.")
    else:
        number_of_jobs_applied = 0
        email_cnt = 0
        for msg in messages:
       
            email_cnt += 1
            email_details = get_email_details(service, msg['id'])
            message_id = email_details['id']

            is_action_needed(email_details, service)
            is_acknowledgment = is_application_acknowledgment(email_details, service)
            if (is_acknowledgment):
                print("Printing isAck == ", is_acknowledgment)
                number_of_jobs_applied += is_acknowledgment
                application_information = extract_application_information(email_details, service)
                remove_from_inbox(service, message_id)
                mark_as_read(service, message_id)
        json_to_excel("all_applications.json")
        delete_json_file("all_applications.json")
            
        print("Number of jobs applied ",number_of_jobs_applied)
        print("Number of messages processed ", email_cnt)

