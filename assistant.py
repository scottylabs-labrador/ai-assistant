"""
A script to update the OpenAI assistant, as well as a library to interact with it
"""

import os
import time
from openai import OpenAI, NotFoundError
from dotenv import load_dotenv

# Constants
ASSISTANT_ID = "asst_ErKdy8h6lM8ia6JqZhD8WXSu"
ASSISTANT_NAME = "Calendar Assistant"
ASSISTANT_INSTRUCTIONS = ""
ASSISTANT_MODEL = "gpt-4"


def thread_create(openai_client):
    """
    Create OpenAI Thread
    """
    return openai_client.beta.threads.create()


def thread_append(openai_client, thread, role, content):
    """
    Append a user prompt to the OpenAI Thread.
    Returns a Message object

    role: "user" or "assistant"
    content: message content
    """
    return openai_client.beta.threads.messages.create(
        thread_id=thread.id, role=role, content=content
    )


def get_response(openai_client, asst, thread):
    """
    Get the response from the assistant
    """
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=asst.id,
    )

    while run.status in ["queued", "in_progress", "cancelling"]:
        time.sleep(1)  # Wait for 1 second
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id
        )

    match run.status:
        case "completed":
            raise NotImplementedError
        case "requires_action":
            # for when we have functions!
            raise NotImplementedError
        case _:
            raise RuntimeError


def retrieve_assistant(openai_client):
    """
    Retrieves the assistant from OpenAI.
    Throws a NotFoundError if the assistant doesn't exist
    """
    asst = openai_client.beta.assistants.retrieve(ASSISTANT_ID)
    return asst


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
