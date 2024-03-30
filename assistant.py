"""
A script to update the OpenAI assistant, as well as a library to interact with it
"""

import os
from openai import OpenAI, NotFoundError
from dotenv import load_dotenv

# Constants
ASSISTANT_ID = "asst_ErKdy8h6lM8ia6JqZhD8WXSu"
ASSISTANT_NAME = "Calendar Assistant"
ASSISTANT_INSTRUCTIONS = ""
ASSISTANT_MODEL = "gpt-4"


def update_assistant(openai_client):
    """
    Updates the info of the agent to what we want it to be
    """

    try:
        asst = openai_client.beta.assistants.retrieve(ASSISTANT_ID)
    except NotFoundError:
        print("Assistant not found! Something's wrong!")
        exit(1)

    assert asst.name == ASSISTANT_NAME

    if asst.instructions != ASSISTANT_INSTRUCTIONS:
        print("Updating instructions...")
        asst = openai_client.beta.assistants.update(
            assistant_id=ASSISTANT_ID, instructions=ASSISTANT_INSTRUCTIONS
        )

    if asst.model != ASSISTANT_MODEL:
        print("Updating model...")
        asst = openai_client.beta.assistants.update(
            assistant_id=ASSISTANT_ID, model=ASSISTANT_MODEL
        )

    print("All good!")


if __name__ == "__main__":
    load_dotenv()

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)

    update_assistant(client)
