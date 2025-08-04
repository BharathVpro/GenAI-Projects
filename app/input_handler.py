"""
Input Handler Module
Manages file uploads, URL inputs, and text input
"""

import streamlit as st

def render_input_section():
    """Render the unified input section and return input values"""
    st.subheader("📝 Insert Unstructured Data")

    # Instructions 
    with st.expander("💡 Instructions", expanded= False):
        st.markdown("""
        **📚 Classic Literature URLs (Project Gutenberg):**
        - Romeo and Juliet: `https://www.gutenberg.org/files/1513/1513-0.txt`
        - Hamlet: `https://www.gutenberg.org/files/1524/1524-0.txt`
        - Pride and Prejudice: `https://www.gutenberg.org/files/1342/1342-0.txt`
        
        **✍️ Or paste sample text:**
        ```
        ROMEO. But soft! What light through yonder window breaks? 
        It is the east, and Juliet is the sun.
        JULIET. O Romeo, Romeo! Wherefore art thou Romeo?
        ```
        """)
    
   
    # URL input option
    url_input = st.text_input(
        "Enter URL (e.g., Project Gutenberg link)",
        placeholder="https://www.gutenberg.org/files/1513/1513-0.txt",
        help="Enter a direct URL to a text file"
    )
    
    # File uploader (will be used for drag and drop)
    uploaded_file = st.file_uploader(
        "Upload",
        type=['txt'],
        help="Drag and drop a .txt file here",
        label_visibility="collapsed"
    )
    
    # Handle file upload
    if uploaded_file is not None and not st.session_state.file_uploaded:
        file_contents = uploaded_file.read().decode("utf-8")
        st.session_state.text_content = file_contents
        st.session_state.file_uploaded = True
        st.success(f"✅ File '{uploaded_file.name}' loaded successfully!")
        st.rerun()
    
    # Reset file_uploaded flag if file is removed
    if uploaded_file is None and st.session_state.file_uploaded:
        st.session_state.file_uploaded = False
    
    # Text area that can also show uploaded content - full width
    text_input = st.text_area(
        "Text input",
        height=300,
        value=st.session_state.text_content,
        placeholder="🎯 Drop a .txt file above, enter a URL, or type/paste your text here...\n\nExample: Lady Juliet gazed longingly at the stars, her heart aching for Romeo...",
        label_visibility="collapsed",
        key="main_text_input"
    )
    
    # Update session state with text input
    if text_input != st.session_state.text_content:
        st.session_state.text_content = text_input
    
    return url_input, text_input

def get_input_source(url_input, text_input):
    """
    Determine the input source and whether we have valid input
    
    Args:
        url_input: URL string from input field
        text_input: Text string from text area
        
    Returns:
        tuple: (input_source, has_input)
    """
    if url_input:
        return url_input, True
    else:
        has_input = len(st.session_state.text_content.strip()) > 0
        return st.session_state.text_content, has_input