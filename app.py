import streamlit as st
import os
from groq import Groq
from PIL import Image
from PyPDF2 import PdfReader

def initialize_groq():
    api_key = st.text_input("Enter your Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)
        st.session_state["groq_client"] = client
        st.success("Successfully authenticated with Groq API!")
        return client
    else:
        st.warning("Please enter your Groq API Key to proceed.")
        return None

# Set up the Streamlit App
st.set_page_config(
    page_title="Indian GST and Tax GPT",
    layout="wide"
)
st.title("Indian GST and Tax GPT ⚡️")
st.caption("Ask any questions regarding Indian GST and taxation policies. 🌟")

# Initialize Groq client
if "groq_client" not in st.session_state:
    client = initialize_groq()
else:
    client = st.session_state["groq_client"]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for additional resources and file uploads
with st.sidebar:
    st.title("Tax Resources")
    st.write("Explore official GST guidelines and tax calculators:")
    st.markdown("- [GST India](https://www.gst.gov.in/)")
    st.markdown("- [Income Tax India](https://www.incometaxindia.gov.in/)")
    st.markdown("- [Tax Calculators](https://www.incometaxindiaefiling.gov.in/)")

    st.title("Upload Tax Documents")
    uploaded_file = st.file_uploader("Upload a PDF or Image related to GST or Taxes", type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            pdf_text = "\n".join([page.extract_text() for page in reader.pages])
            st.session_state["uploaded_content"] = pdf_text
            st.success("PDF content extracted successfully!")
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            st.session_state["uploaded_content"] = "Image uploaded successfully!"

# Main chat interface
chat_placeholder = st.container()

with chat_placeholder:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input handling
prompt = st.chat_input("What do you want to know about GST or taxes in India?")

if prompt:
    # Validate the input to ensure it is related to GST or taxes
    if any(keyword in prompt.lower() for keyword in ["gst", "tax", "income tax", "taxation", "indirect tax", "direct tax"]):
        inputs = [prompt]

        if "uploaded_content" in st.session_state:
            inputs.append(st.session_state["uploaded_content"])

        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # Display user message
        with chat_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Generate and display response
        if client:
            with st.spinner('Generating response...'):
                try:
                    # Set the system role for the AI
                    system_role = (
                        "You are an expert AI specializing in Indian GST and taxation. "
                        "You must only answer questions related to Indian GST, income tax, or related policies. "
                        "Do not answer unrelated questions."
                    )
                    
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_role},
                            {"role": "user", "content": prompt}
                        ],
                        model="deepseek-r1-distill-llama-70b",
                    )
                    response_text = chat_completion.choices[0].message.content

                    # Append a source reference to the response
                    source_note = "\n\n**Source**: This response is based on the official Indian GST guidelines and tax policies. For further details, visit [GST India](https://www.gst.gov.in/) or [Income Tax India](https://www.incometaxindia.gov.in/)."
                    full_response = response_text + source_note

                    with chat_placeholder:
                        with st.chat_message("assistant"):
                            st.markdown(full_response)

                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response
                    })
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please authenticate with the Groq API to proceed.")
    else:
        st.warning("Please ask questions specifically related to GST or taxation in India.")
