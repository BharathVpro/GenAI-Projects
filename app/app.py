"""
Langextract Application
A Streamlit app for advanced text analysis using Google's Langextract
"""

import streamlit as st
from components import setup_page_config, apply_custom_css, render_sidebar, render_header
from input_handler import render_input_section, get_input_source
from processor import process_text
from render_components import render_results

def main():
    """Main application entry point"""
    
    # Setup page configuration
    setup_page_config()
    
    # Apply custom CSS
    apply_custom_css()
    
    # Initialize session state
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'json_data' not in st.session_state:
        st.session_state.json_data = None
    if 'html_content' not in st.session_state:
        st.session_state.html_content = None
    if 'text_content' not in st.session_state:
        st.session_state.text_content = ""
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'analytics' not in st.session_state:
        st.session_state.analytics = None
    
    # Render header
    render_header()
    
    # Render sidebar with advanced settings
    extraction_passes, max_workers, max_char_buffer = render_sidebar()
    
    # Render input section
    url_input, text_input = render_input_section()
    
    # Get input source and check if we have input
    input_source, has_input = get_input_source(url_input, text_input)
    
    # Process button and text processing
    if has_input:
        st.markdown("")  # Add some spacing
        if st.button("🚀 Process Text", type="primary", use_container_width=False):
            progress_container = st.container()
            with progress_container:
                with st.spinner("🔄 Running advanced extraction with multiple passes..."):
                    # Process the text
                    success = process_text(
                        input_source, 
                        extraction_passes, 
                        max_workers, 
                        max_char_buffer
                    )
                    
                    if success:
                        st.success("✅ Advanced processing complete!")
    
    # Display results if available
    if st.session_state.processed and st.session_state.json_data and st.session_state.html_content:
        render_results()
    
    # # Footer
    # st.divider()
    

if __name__ == "__main__":
    main()