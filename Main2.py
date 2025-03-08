import streamlit as st
import os

# Initialize session state if not already initialized
if 'tab' not in st.session_state:
    st.session_state.tab = 'tab1'
    st.session_state.pdf_file = None
    st.session_state.text_from_pdf = None

# Function to handle file upload and process
def process_pdf(uploaded_file):
    # Placeholder for actual PDF processing logic
    # Assuming the text is extracted from the PDF
    return f"Extracted text from {uploaded_file.name}"

# Create tab navigation logic
tabs = ['tab1', 'tab2', 'tab3']

tab = st.radio('Navigate through tabs', tabs, index=tabs.index(st.session_state.tab), key="tab_nav")

# Switch between tabs based on session state
if tab == 'tab1':
    st.session_state.tab = 'tab1'
    
    # Tab 1 content
    st.header('Upload PDF File (Tab 1)')
    
    uploaded_pdf = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_pdf:
        st.session_state.pdf_file = uploaded_pdf
        st.write(f"Uploaded file: {uploaded_pdf.name}")
    
    if st.session_state.pdf_file:
        if st.button("Confirm Upload"):
            st.session_state.tab = 'tab2'
            st.experimental_rerun()  # Forces the app to rerun and switch to Tab 2

elif tab == 'tab2':
    st.session_state.tab = 'tab2'
    
    # Tab 2 content
    st.header('PDF Text Extraction (Tab 2)')
    
    if st.session_state.pdf_file:
        st.session_state.text_from_pdf = process_pdf(st.session_state.pdf_file)
        st.text_area("Extracted Text", st.session_state.text_from_pdf, height=300)
    
    if st.session_state.text_from_pdf:
        if st.button("Next Step"):
            st.session_state.tab = 'tab3'
            st.experimental_rerun()  # Forces the app to rerun and switch to Tab 3

elif tab == 'tab3':
    st.session_state.tab = 'tab3'
    
    # Tab 3 content
    st.header('Download Text File (Tab 3)')
    
    # Provide a link for text download
    if st.session_state.text_from_pdf:
        text_filename = "extracted_text.txt"
        with open(text_filename, 'w') as f:
            f.write(st.session_state.text_from_pdf)
        
        st.download_button("Download Text File", data=open(text_filename, "r").read(), file_name=text_filename)
    
    # Button to start over
    if st.button("Start Over"):
        st.session_state.tab = 'tab1'
        st.session_state.pdf_file = None
        st.session_state.text_from_pdf = None
        st.experimental_rerun()  # Forces the app to rerun and reset

# Logic to disable tabs based on the current state
st.session_state.tab_disabled = {
    'tab1': (st.session_state.tab != 'tab1'),
    'tab2': (st.session_state.tab != 'tab2'),
    'tab3': (st.session_state.tab != 'tab3')
}

# Update tab visibility based on the session state
for t in tabs:
    if st.session_state.tab_disabled[t]:
        st.markdown(f'<style>div[data-baseweb="tab"] >> #{t} {{ pointer-events: none; opacity: 0.5; }}</style>', unsafe_allow_html=True)

