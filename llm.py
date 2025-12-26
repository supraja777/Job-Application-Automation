from langchain_groq import ChatGroq
from dotenv import load_dotenv

from utility import add_label

from langchain_core.prompts import PromptTemplate
load_dotenv()

from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

llm = ChatGroq(model = "llama-3.3-70b-versatile")

class ActionNeeded(BaseModel):
    action_needed: bool = Field(..., description = "true if action is needed, false if not needed")

class Acknowledgment(BaseModel):
    is_application_acknowledgment: bool = Field(..., description = "True if email is an application acknowledgment False if not")


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


# LLM to determine if the email is related to job and no action is needed
# Emails like thanks for applying, we regret to inform that we are going forward
# With other candidates


determine_action_chain = action_template | llm.with_structured_output(ActionNeeded)
application_acknowledgment_chain = application_acknowledgment_template | llm.with_structured_output(Acknowledgment)

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



    