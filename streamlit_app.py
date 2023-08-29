import streamlit as st
from langchain.llms import OpenAI
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.stateful_button import button
import pandas as pd
import openai
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

################   FUNCTIONS  ######################
def get_session_state():
    session = st.session_state
    if "checkbox_state" not in session:
        session.checkbox_state = {}
    return session

# Define a function to update the checkbox state
def update_checkbox_state(row):
    session_state = get_session_state()
    # print(f"Session state before update: {session_state}")
    session_state.checkbox_state[row["Suggest Codes"]] = row["AorR"]
    # print(f"Session state after update: {session_state}")

# Define a function to get the checkbox state
def get_checkbox_state():
    session_state = get_session_state()
    print(f"Get Checkbox Session state: {session_state}")
    if "checkbox_state" not in session_state:
        session_state.checkbox_state = {}
    return session_state.checkbox_state

# Define a function to clear the checkbox state
def clear_checkbox_state():
    session_state = get_session_state()
    if "checkbox_state" in session_state:
        del session_state.checkbox_state


###########################################################

st.set_page_config(page_title="🩺 Medical Billing")
st.header('🩺 Medical Billing Codes Quickstart 🚑')

#Call sidebar function to implement the sidebar
st.set_option('deprecation.showPyplotGlobalUse', False)


temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.1
)
tokens = st.sidebar.slider(
    "Maximum Tokens",
    min_value=64,
    max_value=2048,
    value=256,
    step=64
)

#Side Bar code
with st.sidebar:
  st.markdown(
    "## How to use\n"
    "1. Enter your medical short hand or clinical note into the top box 📝\n"  # noqa: E501
    "2. Optional: Adjust the temperature and tokens to change the output 🌡\n"
    "3. Press submit 👆🏽\n"
    "4. Accept the suggested MBS billing codes ✅\n"
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

openai.api_type = "azure"
openai.api_key = "68454d59782d4c69b9f518d4741351ca"
openai.api_base = 'https://rl-oai01.openai.azure.com/'
openai.api_version = "2023-03-15-preview"

##################################################################################
def generate_codes(question, temperature=temperature, tokens=tokens):

    system_prompt = """
    You are an expert Australian medical practitioner and your role is to review the clinial notes provided by the user and respond with a list of the relevant SNOMED codes and MBS codes
    - Provide multiple codes if they are relevant.
    - Do not provide irrelevant codes. If there are no relevant codes, say "there are no relevant codes".
    Use the following format for your response:
    SNOMED CODE: 
    SNOMED TERM:
    SNOMED CODE: 
    SNOMED TERM:
    SNOMED CODE: 
    SNOMED TERM:
    SNOMED CODE: 
    SNOMED TERM:
    MBS CODE:
    MBS TERM:
    MBS CODE:
    MBS TERM:
    MBS CODE:
    MBS TERM:
    MBS CODE:
    MBS TERM:
    Now please review the user's clinical notes:
    """

    messages = []

    messages.append({"role" : "system", "content" : system_prompt})

    messages.append({"role" : "user", "content" : question})

    response = openai.ChatCompletion.create(
                    engine="chat-gpt35",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=tokens,
                    n=1)
    answer = response.choices[0].message.content
    return answer

def split_codes(data):
    snomed_codes = []
    snomed_terms = []
    mbs_codes = []
    mbs_terms = []
    for line in data.split('\n'):
        if line.startswith('SNOMED CODE:'):
            snomed_codes.append(line.split(': ')[1])
        elif line.startswith('SNOMED TERM:'):
            snomed_terms.append(line.split(': ')[1])
        elif line.startswith('MBS CODE:'):
            mbs_codes.append(line.split(': ')[1])
        elif line.startswith('MBS TERM:'):
            mbs_terms.append(line.split(': ')[1])
    return snomed_codes, snomed_terms, mbs_codes, mbs_terms
##################################################################################
with st.form('my_form'):
  text = st.text_area('Paste in a Clinical Note:', 'The patient is a 24-year-old male who presented to the clinic with an arm wound...')
  submitted = st.form_submit_button('Submit')
  if submitted:
    output_codes = generate_codes(text)
    st.text_area("SNOWMED Code Output", output_codes, height=150)

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
    "Click the checkboxes to accept the relevant MBS codes"
  )
   
  
  #Put the response from the prompt in here
    if submitted:
        grid_key = 'snomed_key'
        snomed_codes, snomed_terms, mbs_codes, mbs_terms = split_codes(output_codes)
        snomed_data = {
        'SNOMED CODES': snomed_codes,
        'SNOMED TERMS': snomed_terms
        }

        df = pd.DataFrame(snomed_data)
        gd = GridOptionsBuilder.from_dataframe(df)
        gd.configure_selection(selection_mode='multiple', use_checkbox=True)
        gridoptions = gd.build()

        grid_table = AgGrid(df, height=250, gridOptions=gridoptions, key=grid_key,
                            update_mode=GridUpdateMode.VALUE_CHANGED)
        selected_rows1 = grid_table['selected_rows']
        print(selected_rows1)


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
    "Click the checkboxes to accept the relevant MBS codes"
  )
    #PRINTING RETURNED MBS CODES
    #Here we want to print a list of the retunred MBS Codes
    if submitted:
        grid_key1 = 'mbs_key'
        snomed_codes, snomed_terms, mbs_codes, mbs_terms = split_codes(output_codes)
        MBS_data = {
        'MBS CODES': mbs_codes,
        'MBS TERMS': mbs_terms
        }
        df1 = pd.DataFrame(MBS_data)
        gd1 = GridOptionsBuilder.from_dataframe(df1)
        gd1.configure_selection(selection_mode='multiple', use_checkbox=True)
        gridoptions1 = gd1.build()

        grid_table1 = AgGrid(df1, height=250, gridOptions=gridoptions1, key=grid_key1,
                            update_mode=GridUpdateMode.VALUE_CHANGED)
        
        selected_rows2 = grid_table1['selected_rows']
    
        print(selected_rows2)

##### Here's the code for downloading the selected rows ########
export = st.button('Download Selected Rows')
if export and submitted:
    selected_rows1 = grid_table['selected_rows']
    selected_rows2 = grid_table1['selected_rows']
    selected_df = st.dataframe(selected_rows1 + selected_rows2)
    print(selected_df)
    csv = selected_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="selected_rows.csv">Download Selected Rows</a>'
    st.markdown(href, unsafe_allow_html=True)































    # Generate a list of 10 random strings, each with a length of 5 characters
    #random_MBS = ["MBS1234","MBS2345", "MBS6789", "MBS0798","MBS4692"]

    #Create and array with procedures
    #procedure_array = ["Brain and Nervous System","Neck and Spine", "Blood", "Blood","Joint and Muscle"]


    # Apply the CheckboxColumn to the "AorR" column of the DataFrame
#     st.data_editor(
#         data_df,
#         column_config={
#             "AorR": st.column_config.CheckboxColumn(
#                 "Click to Accept",
#                 help="Click to Accept or Reject a Code",
#                 default=False,
#             )
#         },
#         disabled=["Suggest Codes"],
#         hide_index=True,
#     )

# # Apply the update_checkbox_state function to each row in the DataFrame
# data_df.apply(update_checkbox_state, axis=1)


# # Get the checkbox state
# checkbox_state = get_checkbox_state()

# # Create an array with the checkbox values
# checkbox_array = [checkbox_state.get(string, False) for string in random_MBS]

# # Display the checkbox array
# st.write(checkbox_array)

# ######## TEST CODES #################

# data = {
#     'MBS': random_MBS,
#     'Procedure': procedure_array
# }

# df = pd.DataFrame(data)
# gd = GridOptionsBuilder.from_dataframe(df)
# gd.configure_selection(selection_mode='multiple', use_checkbox=True)
# gridoptions = gd.build()

# grid_table = AgGrid(df, height=250, gridOptions=gridoptions,
#                     update_mode=GridUpdateMode.SELECTION_CHANGED)

# st.write('## Selected')
# selected_row = grid_table["selected_rows"]
# st.dataframe(selected_row)
