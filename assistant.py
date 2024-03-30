# Constants
ASSISTANT_ID = "asst_ErKdy8h6lM8ia6JqZhD8WXSu"
ASSISTANT_NAME = "Calendar Assistant"
ASSISTANT_INSTRUCTIONS = ""
ASSISTANT_MODEL = "gpt-4"


# Updates the info of the agent to what we want it to be
def update_assistant(client):
    try:
        asst = client.beta.assistants.retrieve(ASSISTANT_ID)
    except NotFoundError:
        print("Assistant not found! Something's wrong!")
        exit(1)

    assert asst.name == ASSISTANT_NAME

    if asst.instructions != ASSISTANT_INSTRUCTIONS:
        print("Updating instructions...")
        asst = client.beta.assistants.update(
            assistant_id=ASSISTANT_ID, instructions=ASSISTANT_INSTRUCTIONS
        )

    if asst.model != ASSISTANT_MODEL:
        print("Updating model...")
        asst = client.beta.assistants.update(
            assistant_id=ASSISTANT_ID, model=ASSISTANT_MODEL
        )

    print("All good!")


if __name__ == "__main__":
    from openai import OpenAI, NotFoundError
    import os
    from dotenv import load_dotenv

    load_dotenv()

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)

    update_assistant(client)
