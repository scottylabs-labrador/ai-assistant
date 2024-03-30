"""
A Streamlit app to interact with Donna
"""

import streamlit as st
from openai import OpenAI, NotFoundError
import assistant


def response_generator():
    """
    Streamed response emulator
    Pre: latest message should be in chat history
    """
    client = st.session_state["openai_client"]
    streamed_response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
    )
    return streamed_response


def setup_openai():
    """
    Set up OpenAI client and model.
    Puts info into st.session_state.{openai_client,openai_model}
    """

    if "openai_client" not in st.session_state:
        # Set OpenAI API key from Streamlit secrets
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        asst = assistant.retrieve_assistant(client)
        thread = assistant.thread_create(client)

        st.session_state["openai_client"] = client
        st.session_state["openai_assistant"] = asst
        st.session_state["openai_thread"] = thread

    assert "openai_assistant" in st.session_state


def app_main():
    """
    Main Streamlit app
    """
    try:
        setup_openai()
    except NotFoundError:
        st.error("Assistant not found! Something's wrong!")
        st.stop()

    st.title("Donna")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(
        "How can I help?" if not st.session_state.messages else ""
    ):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        assistant.thread_append(
            st.session_state["openai_client"],
            st.session_state["openai_thread"],
            "user",
            prompt,
        )

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator())

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        assistant.thread_append(
            st.session_state["openai_client"],
            st.session_state["openai_thread"],
            "assistant",
            response,
        )


app_main()
