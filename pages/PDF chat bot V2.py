import streamlit as st
import pandas as pd
import numpy as np
import fitz
import base64
import os
import io
import time
from dotenv import load_dotenv
from PIL import Image

from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex

########
# INIT #
########
load_dotenv()
st.set_page_config(page_title="PDF chat bot",
                   layout='wide')
st.title("PDF chat bot")
# st.text(os.getenv('LLAMA_CLOUD_API_KEY'))
# st.text(os.getenv('OPENAI_API_KEY'))

if 'container' not in st.session_state:
    st.session_state.container = 1
if 'dfPDF' not in st.session_state:
    st.session_state.dfPDF = None
if 'parsedData' not in st.session_state:
    st.session_state.parsedData = None
if 'indexedData' not in st.session_state:
    st.session_state.indexedData = None

#st.text(st.session_state.container)
###################################################
# CONTAINER1: UPLOAD AND CONVERT TO BASE64 STRING #
###################################################

# FUNCTION TO CONVERT IMAGE TO BASE64
def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# CONTAINER1
if st.session_state.container == 1:
    # HEADER
    st.markdown('<h3 style="color: black;">Step1: Upload PDFs</h3>', unsafe_allow_html=True)
    # UPLOAD FILE AND CONVERT TO B64 IMAGES
    uploadedPDFs = st.file_uploader("Upload multiple PDF files", type=["pdf"], accept_multiple_files=True)
    if uploadedPDFs:
        lsdfPDF = []
        for i in range(len(uploadedPDFs)):            
            uploadedPDF = uploadedPDFs[i]    
            # 
            #st.text(uploadedPDF)
            #st.text(uploadedPDF.getvalue())

            # SHOW NAME
            st.text(f"### FILE {i+1} ###")
            st.text(f">    {uploadedPDF.name}")
            # OPEN THE UPLOADED PDF WITH FITZ
            with fitz.open(stream=uploadedPDF.read(), filetype="pdf") as fitzPDF:
                # SHOW THE NUMBER OF PAGES
                st.text(f">    Number of pages: {fitzPDF.page_count}")
                # CHECK IF PDF IS ENCRYPTED
                if fitzPDF.is_encrypted:
                    # PRINT ENCRYPTED
                    st.text(">    The PDF is locked (encrypted).")
                    # LOG PDF TO DATAFRAME
                    lsdfPDF.append({'PDF_OBJECT': uploadedPDF,
                                    'FILE_NAME': uploadedPDF.name,
                                    'PAGES': fitzPDF.page_count,
                                    'ENCRYPTION': 'Y',
                                    'BASE64':None})
                else:
                    # PRINT NOT ENCRYPTED
                    st.text(">    The PDF is not locked.")
                    # LIST TO STORE BASE64 STRING OF EACH PAGE
                    lsb64Str = []
                    # ITERATE THROUGH EACH PAGE OF THE PDF
                    for page_num in range(fitzPDF.page_count):
                        # LOAD PAGE
                        page = fitzPDF.load_page(page_num)
                        # CONVERT PAGE TO PIXMAP
                        pix = page.get_pixmap()
                        # CONVERT PIXMAP TO PIL IMAGE
                        img = Image.open(io.BytesIO(pix.tobytes()))
                        # CONVERT IMG TO BASE64
                        b64Str = image_to_base64(img)
                        # ADD BASE64 TO LIST
                        lsb64Str.append(b64Str[:100])
                    # LOG PDF TO DATAFRAME
                    lsdfPDF.append({'PDF_OBJECT': uploadedPDF,
                                    'FILE_NAME': uploadedPDF.name,
                                    'PAGES': fitzPDF.page_count,
                                    'ENCRYPTION': 'N',
                                    'BASE64':lsb64Str})

            # 
            st.text(' ')

        # BUILD dfPDF
        dfPDF = pd.DataFrame(lsdfPDF).reset_index(drop=True)
        dfPDF.insert(0, 'NO', np.arange(len(dfPDF))+1)            
        #st.dataframe(dfPDF.astype(str))

        # SHOW NOTICE
        st.text_area(
        "NOTICE",
        f"You uploaded {len(dfPDF)} files\n"
        f"Files Encrypted {len(dfPDF[dfPDF['ENCRYPTION']=='Y'])}\n"
        f"Able to proceed {len(dfPDF[dfPDF['ENCRYPTION']=='N'])}")
        # CONFIM BUTTON
        if st.button("Next Step: Parse PDFs"):
            st.session_state.dfPDF = dfPDF.copy()
            st.session_state.container = 2
            st.rerun()

#################################
# CONTAINER2: PARSING PDF FILES #
#################################

# CONTAINER2
elif st.session_state.container == 2:
    # HEADER
    st.markdown('<h3 style="color: lightgrey;">Step1: Upload PDFs</h3>', unsafe_allow_html=True)
    st.markdown('<h3 style="color: black;">Step2: Parse PDFs</h3>', unsafe_allow_html=True)
    # INIT PARSER
    parser = LlamaParse(result_type="markdown")
    # PREP dfPDF
    dfPDF = st.session_state.dfPDF.copy()
    #st.text('Before Parse')
    #st.dataframe(dfPDF.astype(str))
    # LOOP PARSE
    if st.session_state.parsedData is None:
        lsParsed = []
        for i in range(len(dfPDF)):
            row = dfPDF.iloc[i]
            encrypted = row['ENCRYPTION']
            file_name = row['FILE_NAME']
            uploadedPDF = row['PDF_OBJECT']
            if encrypted == 'Y':
                st.text(f"Parsing {i+1} of {len(dfPDF)} : {file_name}")
                st.text('>    SKIPPED DUE TO ENCRYPTION')
                lsParsed.append(None)
            else:
                st.text(f"Parsing {i+1} of {len(dfPDF)} : {file_name}")
                while True:                                   
                    doc_parsed = parser.load_data(uploadedPDF.getvalue(), extra_info={'file_name':file_name})
                    if len(doc_parsed) == 0:
                        st.text('>    ERROR PARSING PDF, RETRYING')
                        time.sleep(1)
                        continue
                    else:
                        st.text('>    PDF PARSE SUCCESSFUL')
                        lsParsed.append(doc_parsed)
                        break
            time.sleep(2)
        # SAVE SESSION STATE
        st.session_state.parsedData = lsParsed
    else:
        st.text('All PDF Files already Parsed')
        lsParsed = st.session_state.parsedData

    # DATA FRAME
    dfPDF['PARSED'] = lsParsed
    #st.text('After Parse')
    #st.dataframe(dfPDF.astype(str))
    # PARSED DATA
    for i in range(len(dfPDF)):
        file_name = dfPDF['FILE_NAME'].iat[i]
        parsed = dfPDF['PARSED'].iat[i]
        if parsed is not None:
            #st.text(parsed)
            parsed_joined = '\n'.join([x.text for x in parsed])
            #st.code(parsed_joined)
            with st.expander(f"file{i+1}: {file_name}"):
                st.code(parsed_joined)          
    # CONFIM BUTTON
    if st.button("CONFIRM2"):
        st.session_state.dfPDF = dfPDF.copy()
        st.session_state.container = 3
        st.rerun()

####################################
# CONTAINER3: EMBEDDING INTO INDEX #
####################################

# CONTAINER3
elif st.session_state.container == 3:
    # HEADER
    st.markdown('<h3 style="color: lightgrey;">Step1: Upload PDFs</h3>', unsafe_allow_html=True)
    st.markdown('<h3 style="color: lightgrey;">Step2: Parse PDFs</h3>', unsafe_allow_html=True)
    st.markdown('<h3 style="color: black;">Step3: Embedding Parsed PDFs into Index</h3>', unsafe_allow_html=True)
    # PREP dfPDF
    dfPDF = st.session_state.dfPDF.copy()
    #st.text('Before Index')
    #st.dataframe(dfPDF.astype(str))
    # PREP INDEX
    if st.session_state.parsedData is not None:
        lsParsed = st.session_state.parsedData
        lsParsed = [x for x in lsParsed if x is not None]
        st.text(f"Total PDFs {len(lsParsed)}")
        lsParsedJoined = []
        for i in range(len(lsParsed)):
            parsed = lsParsed[i]
            st.text(f">    PDF {i+1} have {len(parsed)} pages")
            lsParsedJoined = lsParsedJoined + lsParsed[i]
        st.text(f"Total Pages {len(lsParsedJoined)}")
    # INDEX
    if st.session_state.indexedData is None:
        st.text('Indexing Status: Indexing Data')
        indexedData = VectorStoreIndex.from_documents(lsParsedJoined)
        st.text('Indexing Status: Indexing Successful')
        st.session_state.indexedData = indexedData
    else:
        st.text('Indexing Status: Already Indexed Data')
        indexedData = st.session_state.indexedData
    # CONFIM BUTTON
    if st.button("Go to chat"):
        st.session_state.dfPDF = dfPDF.copy()
        st.session_state.container = 4
        st.rerun()

#######################
# CONTAINER4: CHATBOX #
#######################

# CONTAINER4
elif st.session_state.container == 4:
    # HEADER
    st.markdown('<h3 style="color: lightgrey;">Step1: Upload PDFs</h3>', unsafe_allow_html=True)
    st.markdown('<h3 style="color: lightgrey;">Step2: Parse PDFs</h3>', unsafe_allow_html=True)
    st.markdown('<h3 style="color: lightgrey;">Step3: Embedding Parsed PDFs into Index</h3>', unsafe_allow_html=True)
    st.markdown('<h3 style="color: black;">Step4: Chat with your PDFs</h3>', unsafe_allow_html=True)

    # PREP OPENAI
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    # PREP QUERY ENGINE
    indexedData = st.session_state.indexedData
    query_engine = indexedData.as_query_engine()

    # PREPARE BLANK MESSAGE LIST
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # DISPLAY CHAT HISTORY
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # WHENEVER THERE IS CHAT INPUT
    if userPrompt := st.chat_input("Ask away"):

        # ADD USER PROMPT TO MESSAGE LIST
        st.session_state.messages.append({"role": "user", "content": userPrompt})
        # TRIGGER USER PROMPT TO DISPLAY
        with st.chat_message("user"):
            st.markdown(userPrompt)

        ### ASKING CHATGPT TO FORMULATE QUESTION TO RAG
        # FIRST LOOP
        if len(st.session_state.messages) == 1: 
            # ASK THE PDF ENGINE
            pdfResponse = str(query_engine.query(userPrompt)) 
            # ADD SYSTEM RESPONSE TO MESSAGE LIST
            st.session_state.messages.append({'role': 'system', 'content': pdfResponse})   
            # TRIGGER SYSTEM RESPONSE TO DISPLAY
            with st.chat_message("system"):
                st.markdown(pdfResponse)
        # OTHER LOOP
        else:
            # GET HISTORICAL CHAT EXCEPT LATEST USER PROMPT
            histmsg = st.session_state.messages[:-1]
            # ASK CHATGPT TO FORMULATE QUESTION TO THE RAG ENGINE
            infoForGptToGenerateRagPrompt = f"""
            ### USER PROMPT ###
            {userPrompt}
            ### INSTRUCTION ###
            Formulate the question to ask the RAG engine from the given historical chat and latest user prompt
            note that RAG engine does not have knowledge about historical conversation of this chat
            """
            histmsg.append({"role": "user", "content": infoForGptToGenerateRagPrompt})
            gptPromptForRag = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=histmsg)    
            gptPromptForRag = gptPromptForRag.choices[0].message.content

            # SEE THE RAG PROMPT
            with st.chat_message("ragPrompt"):
                st.markdown(gptPromptForRag)


            # USE THE GPT PROMPT FOR RAG TO ASK RAG ENGINE
            pdfResponse = str(query_engine.query(gptPromptForRag)) 
            # ADD SYSTEM RESPONSE TO MESSAGE LIST
            st.session_state.messages.append({'role': 'system', 'content': pdfResponse}) 
            # TRIGGER SYSTEM RESPONSE TO DISPLAY
            with st.chat_message("system"):
                st.markdown(pdfResponse)

        # GET RESPONSE FROM CHATGPT
        clientResponse = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=st.session_state.messages)
        gptResponse = clientResponse.choices[0].message.content
        # ADD GPT RESPONSE TO MESSAGE LIST
        st.session_state.messages.append({'role': 'assistant', 'content': gptResponse})   
        # TRIGGER SYSTEM RESPONSE TO DISPLAY
        with st.chat_message("assistant"):
            st.markdown(gptResponse)

    # ADD CLEAR CHAT BUTTON
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    #st.json(st.session_state.messages)
