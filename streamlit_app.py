import streamlit as st
from langchain.llms import OpenAI
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.stateful_button import button
import pandas as pd
import random

st.set_page_config(page_title="🩺 Medical Billing")
st.header('🩺 Medical Billing Codes Quickstart 🚑')

#Call sidebar function to implement the sidebar
st.set_option('deprecation.showPyplotGlobalUse', False)

#Side Bar code
with st.sidebar:
  st.markdown(
    "## How to use\n"
    "1. Enter your medical short hand or clinical note into the top box 📝\n"  # noqa: E501
    "2. Press submit 👆🏽\n"
    "3. Accept or Reject the suggest MBS billing codes ✅\n"
  )
  st.markdown("---")
  st.markdown("# About")
  st.markdown(
      "This accelerator was designed for Australian Healthcare customers"
      " to leverage AI for the generation of medical billing codes."
  )
  st.markdown(
      "This tool is a work in progress. "
      "You can contribute to the project on [GitHub](https://github.com/courtney-withers/OpenAI_MBSCodes) "  # noqa: E501
      "with your feedback and suggestions💡"
  )
  st.markdown("Made by the Australian Microsoft Healthcare Team")
  st.markdown("---")

openai_api_key = "abcdefg"

def generate_response(input_text):
  llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
  st.info(llm(input_text))

with st.form('my_form'):
  text = st.text_area('Paste in a Clinical Note:', 'The patient is a 24-year-old male who presented to the clinic with an arm wound...')
  submitted = st.form_submit_button('Submit')
  if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    generate_response(text)

#This is the container which will contain the SNOWMED code response
with stylable_container(
    key="container_with_border",
    css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: calc(1em - 1px)
        }
        """,
):
    
    st.markdown(
    "#### SNOWMED Code Output  \n"
    "These are the corresponding SNOWMED codes to the input text."
  )
  
  #Put the response from the prompt in here

#This is the container which will contain the MBS code response
with stylable_container(
    key="container_with_border",
    css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: calc(1em - 1px)
        }
        """,
):
    
    st.markdown(
    "#### MBS Code Selection  \n"
    "Click the buttons to accept or reject the relevant MBS codes"
  )
    
    #PRINTING RETURNED MBS CODES
    #Here we want to print a list of the retunred MBS Codes
    #Splite the container into columns for better formatting
    col1, col2 = st.columns([3, 1])

    #Generate a random array of codes
    # Define a list of possible characters for the strings
    characters = "1234567890"

    # Generate a list of 10 random strings, each with a length of 5 characters
    random_strings = ["MBS" + ''.join(random.choices(characters, k=5)) for _ in range(10)]
    accept_reject_array = [False] * len(random_strings)

    data_df = pd.DataFrame(
        {
            "Suggest Codes": random_strings,
            "Accept or Reject": accept_reject_array,
        }
    )

    st.data_editor(
        data_df,
        column_config={
            "Accept or Reject": st.column_config.CheckboxColumn(
                "Click to Accept",
                help="Click to Accept or Reject a Code",
                default=False,
            )
        },
        disabled=["widgets"],
        hide_index=True,
    )
