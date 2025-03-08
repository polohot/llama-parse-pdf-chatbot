import streamlit as st
import pandas as pd
import numpy as np
import fitz
import base64
import os
import io
from PIL import Image

st.set_page_config(page_title="PDF chat bot")
st.title("PDF chat bot")

########
# INIT #
########

if 'container' not in st.session_state:
    st.session_state.container = 1

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
    with st.container():
        # HEADER
        st.markdown('<h2 style="color: black;">Step1: Upload PDFs</h2>', unsafe_allow_html=True)
        # UPLOAD FILE AND CONVERT TO B64 IMAGES
        uploadedPDFs = st.file_uploader("Upload multiple PDF files", type=["pdf"], accept_multiple_files=True)
        if uploadedPDFs:
            lsdfPDF = []
            for uploadedPDF in uploadedPDFs:
                # SHOW NAME
                st.text(uploadedPDF.name)
                # OPEN THE UPLOADED PDF WITH FITZ
                with fitz.open(stream=uploadedPDF.read(), filetype="pdf") as fitzPDF:
                    # SHOW THE NUMBER OF PAGES
                    st.write(f"Number of pages: {fitzPDF.page_count}")
                    # CHECK IF PDF IS ENCRYPTED
                    if fitzPDF.is_encrypted:
                        # PRINT ENCRYPTED
                        st.write("The PDF is locked (encrypted).")
                        # LOG PDF TO DATAFRAME
                        lsdfPDF.append({'FILE_NAME': uploadedPDF.name,
                                        'PAGES': fitzPDF.page_count,
                                        'ENCRYPTION': 'Y',
                                        'BASE64':None})
                    else:
                        # PRINT NOT ENCRYPTED
                        st.write("The PDF is not locked.")
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
                        lsdfPDF.append({'FILE_NAME': uploadedPDF.name,
                                        'PAGES': fitzPDF.page_count,
                                        'ENCRYPTION': 'N',
                                        'BASE64':lsb64Str})

                # 
                st.text(' ')
            # SHOW PDF
            dfPDF = pd.DataFrame(lsdfPDF)
            dfPDF.insert(0, 'NO', np.arange(len(dfPDF))+1)
            st.dataframe(dfPDF[['NO','FILE_NAME','PAGES','ENCRYPTION']], hide_index=True)
            # SHOW NOTICE
            st.text_area(
            "NOTICE",
            f"You uploaded {len(dfPDF)} files\n"
            f"Files Encrypted {len(dfPDF[dfPDF['ENCRYPTION']=='Y'])}\n"
            f"Able to proceed {len(dfPDF[dfPDF['ENCRYPTION']=='N'])}")
            # CONFIM BUTTON
            if st.button("CONFIRM"):
                st.session_state.container = 2
                st.rerun()

##################################################
# CONTAINER2: #
##################################################

# CONTAINER2
elif st.session_state.container == 2:
    with st.container():
        st.markdown('<h2 style="color: lightgrey;">Step1: Upload PDFs</h2>', unsafe_allow_html=True)
        st.markdown('<h2 style="color: black;">Step2: encodind</h2>', unsafe_allow_html=True)




        st.text('HEHEHAHA')

        # CONFIM BUTTON
        if st.button("CONFIRM"):
            st.session_state.container = 3
            st.rerun()

# CONTAINER3
elif st.session_state.container == 3:
    with st.container():
        st.text('HEHEHAHA HEHEHAHA')







# if 'container' not in st.session_state:
#     st.session_state.container = 1

# # CONTAINER1
# if st.session_state.container == 1:
#     with st.container():
#         st.text("This is container 1: Text1")
#         if st.button("Button1"):
#             st.session_state.container = 2
#             st.rerun()

# # CONTAINER2
# elif st.session_state.container == 2:
#     with st.container():
#         st.text("This is container 2: Text2")
#         if st.button("Button2"):
#             st.session_state.container = 3
#             st.rerun()

# # CONTAINER3
# elif st.session_state.container == 3:
#     with st.container():
#         st.text("This is container 3: Text3")
#         if st.button("Button3"):
#             st.session_state.container = 1 
#             st.rerun()



# if buttonConfirm1:
#     # TITLE
#     st.title("Echo Bot")
#     # INITIALIZE CHAT HISTORY
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#     # DISPLAY CHAT MESSAGES FROM HISTORY ON APP RETURN
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
#     # REACT TO USER UNPUT
#     if prompt := st.chat_input("What is up?"):
#         # DISPLAY USER MESSAGE IN CHAT MESSAGE CONTAINER
#         with st.chat_message("user"):
#             st.markdown(prompt)
#         # ADD USER MESSAGE TO CHAT HISTORY
#         st.session_state.messages.append({"role": "user", "content": prompt})

#     # response = f"Echo: {prompt}"
#     # # Display assistant response in chat message container
#     # with st.chat_message("assistant"):
#     #     st.markdown(response)
#     # # Add assistant response to chat history
#     # st.session_state.messages.append({"role": "assistant", "content": response})




# # Initialize session state to track which container is visible
# if 'container1_visible' not in st.session_state:
#     st.session_state.container1_visible = True

# # Container 1
# if st.session_state.container1_visible:
#     with st.container():
#         st.write("Text 1")
#         if st.button("Button 1"):
#             st.session_state.container1_visible = False

# # Container 2
# if not st.session_state.container1_visible:
#     with st.container():
#         st.write("Text 2")
#         if st.button("Button 2"):
#             st.session_state.container1_visible = True


