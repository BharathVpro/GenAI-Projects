"""
UI Components Module
Handles page configuration, styling, and UI components
"""

import streamlit as st

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Langextract Demo - Advanced",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def apply_custom_css():
    """Apply custom CSS styling for the application"""
    st.markdown("""
    <style>
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 16px;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab-list"] button {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #FF4B4B;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 1rem;
        }
        .element-container iframe {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
        }
        
        /* Hide the file uploader label */
        [data-testid="stFileUploadDropzone"] > div:first-child {
            display: none;
        }
        
        /* Style file uploader drop zone */
        section[data-testid="stFileUploadDropzone"] > div:nth-child(2) {
            background-color: #fafafa !important;
            border: 2px dashed #cccccc !important;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
        }
        
        section[data-testid="stFileUploadDropzone"] > div:nth-child(2):hover {
            border-color: #FF4B4B !important;
            background-color: #fff5f5 !important;
        }
        
        /* Fix text area to fill container */
        .stTextArea textarea {
            width: 100% !important;
            resize: vertical !important;
        }
        
        .stTextArea > div > div {
            width: 100% !important;
        }
        
        /* Fix metric styling for dark theme */
        [data-testid="metric-container"] {
            background-color: rgba(240, 242, 246, 0.5);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid rgba(49, 51, 63, 0.2);
        }
        
        /* Ensure metric values are visible in dark theme */
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: var(--text-color, #262730) !important;
        }
        
        @media (prefers-color-scheme: dark) {
            [data-testid="metric-container"] {
                background-color: rgba(49, 51, 63, 0.5);
                border: 1px solid rgba(250, 250, 250, 0.2);
            }
            
            [data-testid="metric-container"] [data-testid="stMetricValue"] {
                color: #FAFAFA !important;
            }
            
            [data-testid="metric-container"] [data-testid="stMetricLabel"] {
                color: #FAFAFA !important;
            }
        }
        
        /* Dark theme specific styles */
        .stApp[data-theme="dark"] [data-testid="metric-container"] {
            background-color: rgba(49, 51, 63, 0.5);
            border: 1px solid rgba(250, 250, 250, 0.2);
        }
        
        .stApp[data-theme="dark"] [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #FAFAFA !important;
        }
        
        .stApp[data-theme="dark"] [data-testid="metric-container"] [data-testid="stMetricLabel"] {
            color: #FAFAFA !important;
        }
        
        /* Remove vertical stacking from columns */
        section.main > div {
            max-width: 100%;
        }
        
        /* Ensure full width for input container */
        .row-widget.stTextArea {
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the application header"""
    st.title("🔍 LangExtract")
    st.markdown("##### An AI-powered extractor which can identify characters, emotions and relationships in any text using Google LangExtract, outputting schema-validated JSON with exact character-level source grounding and optimized handling of long documents")
    st.divider()

def render_sidebar():
    """Render sidebar with advanced settings and return configuration values"""
    with st.sidebar:
        st.header("⚙️ Advanced Settings")
        
        extraction_passes = st.slider(
            "Extraction Passes",
            min_value=1,
            max_value=5,
            value=3,
            help="Number of passes through the text for better recall"
        )
        
        max_workers = st.slider(
            "Parallel Workers",
            min_value=1,
            max_value=30,
            value=20,
            help="Number of parallel workers for faster processing"
        )
        
        max_char_buffer = st.slider(
            "Context Window Size",
            min_value=500,
            max_value=2000,
            value=1000,
            step=100,
            help="Size of text chunks for analysis"
        )
        
        st.divider()
        st.markdown("### About Advanced Mode")
        st.info("""
        🚀 **Advanced features enabled:**
        - Multi-pass extraction for better accuracy
        - Parallel processing for speed
        - Optimized context windows
        - Character analytics & insights
        - Support for large documents
        """)
        
    return extraction_passes, max_workers, max_char_buffer