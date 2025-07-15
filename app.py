import streamlit as st
from dotenv import load_dotenv
import os

# Import components
from auth import auth_component, check_authentication, get_current_user, logout
from components.simple_prospect import simple_prospect_component
from components.ai_report import ai_report_component
from database.models import db

# Load environment variables
load_dotenv()

# Page configuration with NBP branding
st.set_page_config(
    page_title="NBP - Sales Preparation Tool",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Hyper Baraaq branding with red and white theme
def load_custom_css():
    st.markdown("""
    <style>
    /* Hyper Baraaq Branding Colors - Red and White Only */
    :root {
        --primary-red: #ff0000;
        --white: #ffffff;
        --light-gray: #f8f8f8;
        --dark-gray: #333333;
        --success-green: #28a745;
        --warning-orange: #ffc107;
    }
    
    /* Modern Container Styling */
    .main-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(255,0,0,0.1);
        border: 1px solid rgba(255,0,0,0.1);
    }
    
    /* Enhanced Header Styling */
    .main-header {
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
        padding: 2rem 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(255,0,0,0.3);
        border: 3px solid #ff0000;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95);
        text-align: center;
        margin: 1rem 0 0 0;
        font-size: 1.3rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    /* Modern Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(255,0,0,0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #cc0000 0%, #aa0000 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(255,0,0,0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Enhanced Success/Error Messages */
    .success-message {
        background: linear-gradient(135deg, var(--success-green) 0%, #20c997 100%) !important;
        color: white !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 8px 25px rgba(40,167,69,0.3) !important;
        border: 2px solid var(--success-green) !important;
        position: relative;
        overflow: hidden;
    }
    
    .success-message::before {
        content: '✅';
        position: absolute;
        right: 1rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 2rem;
        opacity: 0.3;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ff0000 0%, #dc3545 100%) !important;
        color: white !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 8px 25px rgba(255,0,0,0.3) !important;
        border: 2px solid #ff0000 !important;
        position: relative;
        overflow: hidden;
    }
    
    .error-message::before {
        content: '❌';
        position: absolute;
        right: 1rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 2rem;
        opacity: 0.3;
    }
    
    /* Red background text styling */
    .red-bg-text {
        color: white !important;
    }
    
    .red-bg-text h1, .red-bg-text h2, .red-bg-text h3, .red-bg-text h4, .red-bg-text h5, .red-bg-text h6 {
        color: white !important;
    }
    
    .red-bg-text p, .red-bg-text div, .red-bg-text span {
        color: white !important;
    }
    
    /* Modern Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, white 0%, #f8f9fa 100%) !important;
        border-right: 2px solid rgba(255,0,0,0.1) !important;
    }
    
    .css-1d391kg .stSelectbox > div > div {
        border: 2px solid rgba(255,0,0,0.2) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        background: white !important;
    }
    
    .css-1d391kg .stSelectbox > div > div:focus {
        border-color: #ff0000 !important;
        box-shadow: 0 0 0 3px rgba(255,0,0,0.1) !important;
        transform: scale(1.02) !important;
    }
    
    /* Enhanced Input Fields */
    .stTextInput > div > div > input {
        border: 2px solid rgba(255,0,0,0.2) !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: #333333 !important;
        padding: 0.8rem 1rem !important;
        font-size: 1rem !important;
        background: white !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff0000 !important;
        box-shadow: 0 0 0 3px rgba(255,0,0,0.1) !important;
        transform: scale(1.02) !important;
    }
    
    .stTextInput > div > div > input:hover {
        border-color: rgba(255,0,0,0.5) !important;
    }
    
    /* Enhanced Form Submit Buttons */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px rgba(255,0,0,0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #cc0000 0%, #aa0000 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(255,0,0,0.4) !important;
    }
    
    /* Modern Background */
    .main .block-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        padding: 2rem !important;
    }
    
    /* Enhanced Text Colors */
    h1 {
        color: #ff0000 !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(255,0,0,0.1) !important;
    }
    
    h2, h3, h4, h5, h6 {
        color: #333333 !important;
        font-weight: 600 !important;
    }
    
    /* Modern Links */
    a {
        color: #ff0000 !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
    }
    
    a:hover {
        color: #cc0000 !important;
        text-decoration: underline !important;
    }
    
    /* Enhanced Streamlit Elements */
    .stMarkdown, .stText {
        color: #333333 !important;
        line-height: 1.6 !important;
    }
    
    /* Modern Form Labels */
    .stTextInput > div > div > label,
    .stSelectbox > div > div > label,
    .stTextArea > div > div > label,
    .stFileUploader > div > div > label,
    .stCheckbox > div > div > label,
    .stRadio > div > div > label,
    .stNumberInput > div > div > label,
    .stDateInput > div > div > label,
    .stTimeInput > div > div > label {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Enhanced Sidebar Text */
    .css-1d391kg p, .css-1d391kg div, .css-1d391kg span {
        color: #333333 !important;
    }
    
    /* Modern Cards */
    .info-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,0,0,0.3);
        border-radius: 50%;
        border-top-color: #ff0000;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Success/Error message text */
    .success-message p, .error-message p {
        color: white !important;
        margin: 0 !important;
    }
    
    .success-message h4, .error-message h4 {
        color: white !important;
        margin: 0 0 0.5rem 0 !important;
    }
    
    /* Modern Progress Bars */
    .stProgress > div > div > div > div {
        background-color: #ff0000 !important;
    }
    
    /* Enhanced Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255,0,0,0.1) 0%, rgba(255,0,0,0.05) 100%) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,0,0,0.2) !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        border-radius: 0 0 10px 10px !important;
        border: 1px solid rgba(255,0,0,0.1) !important;
        border-top: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'page' not in st.session_state:
        st.session_state.page = "New Prospect"

def display_header():
    """Display NBP branded header"""
    st.markdown("""
    <div class="main-header">
        <h1>🏢 NBP Sales Preparation Tool</h1>
        <p>Simple Prospect Management and AI Report Generation</p>
    </div>
    """, unsafe_allow_html=True)

def display_user_welcome():
    """Display user welcome message and logout button"""
    current_user = get_current_user()
    if current_user:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div class="info-card red-bg-text" style="background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%); color: white; border: none; box-shadow: 0 10px 30px rgba(255,0,0,0.3);">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 3rem;">👋</div>
                    <div>
                        <h3 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700;">Welcome back, {current_user['username']}!</h3>
                        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">Ready to create prospects and generate AI reports for NBP.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True, help="Sign out of your account"):
                logout()
                st.rerun()

def display_navigation():
    """Display modern navigation with enhanced UX"""
    st.sidebar.markdown("""
    <div class="red-bg-text" style="background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; 
                border: 2px solid #ff0000; box-shadow: 0 8px 25px rgba(255,0,0,0.3);">
        <h3 style="margin: 0; text-align: center; font-size: 1.3rem; font-weight: 700; color: white;">📋 Navigation</h3>
        <p style="margin: 0.5rem 0 0 0; text-align: center; opacity: 0.9; font-size: 0.9rem; color: white;">Choose your next action</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced navigation menu with icons and descriptions
    navigation_options = [
        {
            "icon": "➕",
            "title": "New Prospect",
            "description": "Create a new prospect profile",
            "value": "New Prospect"
        },
        {
            "icon": "🤖",
            "title": "AI Report Generation",
            "description": "Generate AI-powered sales reports",
            "value": "AI Report Generation"
        }
    ]
    
    # Create custom navigation buttons
    for option in navigation_options:
        is_active = st.session_state.page == option["value"]
        active_style = "background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%); color: white; border: 2px solid #ff0000;" if is_active else "background: white; color: #333; border: 2px solid rgba(255,0,0,0.2);"
        
        st.sidebar.markdown(f"""
        <div style="{active_style} padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; 
                    transition: all 0.3s ease; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; gap: 0.8rem;">
                <div style="font-size: 1.5rem;">{option['icon']}</div>
                <div>
                    <div style="font-weight: 600; font-size: 1rem;">{option['title']}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">{option['description']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Use selectbox for actual navigation (hidden but functional)
    page = st.sidebar.selectbox(
        "Select Page",
        options=[opt["value"] for opt in navigation_options],
        index=[opt["value"] for opt in navigation_options].index(st.session_state.page) if st.session_state.page in [opt["value"] for opt in navigation_options] else 0,
        label_visibility="collapsed"
    )
    
    # Update session state
    st.session_state.page = page
    
    # Add helpful tips in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background: rgba(255,0,0,0.05); padding: 1rem; border-radius: 10px; border: 1px solid rgba(255,0,0,0.2);">
        <h4 style="margin: 0 0 0.5rem 0; color: #ff0000; font-size: 1rem;">💡 Quick Tips</h4>
        <ul style="margin: 0; padding-left: 1.2rem; font-size: 0.9rem; color: #666;">
            <li>Create prospects first</li>
            <li>Then generate AI reports</li>
            <li>Download PDFs for meetings</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    return page

def display_success_message(message):
    """Display a styled success message"""
    st.markdown(f"""
    <div class="success-message">
        <h4>✅ Success!</h4>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)

def display_error_message(message):
    """Display a styled error message"""
    st.markdown(f"""
    <div class="error-message">
        <h4>❌ Error</h4>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)

# Main application logic
def main():
    """Main application function with simplified UI"""
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Check authentication
    if not check_authentication():
        return
    
    # Display header
    display_header()
    
    # Get current user
    current_user = get_current_user()
    if not current_user:
        display_error_message("User not authenticated")
        return
    
    # Display user welcome
    display_user_welcome()
    
    # Display navigation
    page = display_navigation()
    
    # Route to appropriate component with enhanced error handling
    try:
        if page == "New Prospect":
            simple_prospect_component()
        elif page == "AI Report Generation":
            ai_report_component()
        else:
            st.error("Page not found")
    
    except Exception as e:
        display_error_message(f"An error occurred: {str(e)}")
        st.error("Please try refreshing the page or contact support if the issue persists.")

if __name__ == "__main__":
    main() 