from langchain_groq import ChatGroq
from dotenv import load_dotenv

from utility import add_label

from langchain_core.prompts import PromptTemplate
load_dotenv()

from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

llm = ChatGroq(model = "llama-3.3-70b-versatile")

class ActionNeeded(BaseModel):
    action_needed: bool = Field(..., description = "Yes if action is needed, no if not needed")

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


# LLM to determine if the email is related to job and no action is needed
# Emails like thanks for applying, we regret to inform that we are going forward
# With other candidates


determine_action_chain = action_template | llm.with_structured_output(ActionNeeded)

def determine_action_needed(email_details, service):
    input_data = {"email_snippet" : email_details}
    isActionNeeded = determine_action_chain.invoke(input_data).action_needed
    print(isActionNeeded)
    if (isActionNeeded):
        message_id = email_details['id']
        add_label(service, message_id, label_name="Action")
    