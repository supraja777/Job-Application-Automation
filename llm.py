from langchain_groq import ChatGroq
from dotenv import load_dotenv

from utility import add_label
import json

from load_data import dump_application_information

from langchain_core.prompts import PromptTemplate
load_dotenv()

from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

llm = ChatGroq(model = "llama-3.3-70b-versatile")

class ActionNeeded(BaseModel):
    action_needed: bool = Field(..., description = "true if action is needed, false if not needed")

class Acknowledgment(BaseModel):
    is_application_acknowledgment: bool = Field(..., description = "True if email is an application acknowledgment False if not")

class ApplicationInformation(BaseModel):
       Date: str = Field(..., description="Date applied")
       company: str = Field(..., description = "Company name to which the job is applied to, example - Oracle, Google"),
       role: str = Field(..., description = "Job role applied to, example - AI/ML Systems Research Intern"),
       job_id_or_link: str = Field(..., description="Job link"),
       resume_attached: str = Field(..., description="returns true if resume is attached, else false")

action_template = PromptTemplate(
    input_variables = ["email_snippet"],
    template = """You are an email assistant that classifies job-related emails.

        If the email is not related to any job application you will respond False
    
        Task:
        Determine if any action is required based on the email snippet.
        Action examples include: replying, scheduling an interview, submitting documents, or completing assessments.

        Instructions:
        - If action is needed, respond ONLY with: true
        - If no action is needed, respond ONLY with: false

        - Do not include any extra text or explanation.

        Email snippet: {email_snippet}

        ActionNeeded :
 
    """
)


application_acknowledgment_template = PromptTemplate(
    input_variables = ["email_snippet"],
    template = """
        You are an email classifier.

        Determine whether the following email is a **job application acknowledgment**.

        Definition:
        A job application acknowledgment email ONLY confirms that a job application was received (e.g., "Thank you for applying", "We have received your application").

        Rules:
       - Set is_application_acknowledgment = true if the email confirms receipt of the application,
        even if it mentions review or future updates,
        as long as no action is required from the applicant.
        - If it includes interviews, rejections, next steps, or actions, set is_application_acknowledgment = false.
        
        Email snippet: {email_snippet}
    """
)

extract_application_information_template = PromptTemplate(
    input_variables =  ["email_snippet", "date", "email_from", "subject"],
    template = """
        You are a structured email parser.

        Extract the following information from the email snippet provided in `email_snippet`:

        Suggestions:
            Try to look for date in date
            Try to look for company name in email_from and then in subject
            Try to look for role first in subject
            Try to look for job_id_or_link first in subject

        - company: Extract the company name from sender, subject, or body.
        - role: Extract the role applied to from subject or body.
        - date_applied: Extract the date applied; if not in snippet, leave empty.
        - job_id_or_link: Extract any job ID or link if present; else leave empty.
        - resume_attached: true if the email mentions an attachment, else false.

       Date: {date}
       Email snippet: {email_snippet}
       email_from : {email_from}
       subject : {subject}

    """
)


determine_action_chain = action_template | llm.with_structured_output(ActionNeeded)
application_acknowledgment_chain = application_acknowledgment_template | llm.with_structured_output(Acknowledgment)
extract_application_information_chain = extract_application_information_template | llm.with_structured_output(ApplicationInformation)

def is_action_needed(email_details, service):
    input_data = {"email_snippet" : email_details}
    isActionNeeded = determine_action_chain.invoke(input_data).action_needed
    print(isActionNeeded)
    if (isActionNeeded):
        message_id = email_details['id']
        add_label(service, message_id, label_name="Action")


def is_application_acknowledgment(email_details, service):
    input_data = {"email_snippet" : email_details}
    isAck = application_acknowledgment_chain.invoke(input_data).is_application_acknowledgment
    print(isAck, email_details)
    if not isAck:
        return False
   
    print("Can be moved to application-acknowledgment folder")
    message_id = email_details['id']
    add_label(service, message_id, label_name="application-acknowledgment")
    return True

def extract_application_information(email_details, service):
    print("In extract application information")

    date = email_details['date']
    email_from = email_details['from']
    subject = email_details['subject']

    input_data = {
        "date": date,
        "email_snippet" : email_details,
        "email_from" : email_from,
        "subject" : subject
    }

    application_information = extract_application_information_chain.invoke(input_data)
    print("Application information - ", application_information)
    print("Dumping in json")
    dump_application_information(application_information)
    return application_information
    




    