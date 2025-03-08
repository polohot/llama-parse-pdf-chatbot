import streamlit as st

st.set_page_config(page_title="Main")

st.title('LLM chatbot iterations')

bodyV1 = '''
V1 - 2025-03-07

First Version using llamaparse then input to openAI chatbot API
Mostly showing debug values

Step1: input PDF file
Step2: Parse PDF using llamaparse
Step3: Indexing/Embedding
Step4: Chat
'''
st.code(bodyV1)

bodyV2 = '''
V2 - 2025-03-08

Cleaner frontend, hiding some unnecessary dataframes or text

Add another gpt to help refine the questions before asking the RAG bot, this is due to the RAG bot have no historical chat data to refer to
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

Fixed hallucination where AI confuse between 2 files, reason because we use the same file name for all document
    Before : doc_parsed = parser.load_data(uploadedPDF.getvalue(), extra_info={'file_name':'_'})
    After  : doc_parsed = parser.load_data(uploadedPDF.getvalue(), extra_info={'file_name':file_name})
'''
st.code(bodyV2)
