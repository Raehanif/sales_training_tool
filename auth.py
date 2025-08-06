import streamlit as st
from typing import Optional, Dict, Any
import base64
from PIL import Image
import os

class AuthManager:
    """Authentication manager for NBP Sales Preparation Tool with hardcoded credentials"""
    
    def __init__(self):
        # Hardcoded credentials
        self.valid_credentials = {
            "sales_rep": "nbp2025"
        }
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate a user with hardcoded credentials"""
        if not username or not password:
            return {"success": False, "message": "Username and password are required"}
        
        # Check against hardcoded credentials
        if username in self.valid_credentials and self.valid_credentials[username] == password:
            return {
                "success": True, 
                "message": "Login successful!",
                "user": {
                    "id": 1,
                    "username": username,
                    "email": "sales_rep@nbp.com",
                    "role": "sales_rep"
                }
            }
        else:
            return {"success": False, "message": "Invalid username or password"}
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username (hardcoded)"""
        if username in self.valid_credentials:
            return {
                "id": 1,
                "username": username,
                "email": "sales_rep@nbp.com",
                "role": "sales_rep",
                "created_at": "2024-01-01"
            }
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID (hardcoded)"""
        if user_id == 1:
            return {
                "id": 1,
                "username": "sales_rep",
                "email": "sales_rep@nbp.com",
                "role": "sales_rep",
                "created_at": "2024-01-01"
            }
        return None

# Global auth instance
auth = AuthManager()

def get_image_base64(image_path: str) -> str:
    """Convert image to base64 for embedding in HTML"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return encoded_string
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return ""

def create_custom_login_page():
    """Create a beautiful custom login page with red and white theme"""
    
    # Custom CSS for the login page
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #ffffff 0%, #f8f8f8 100%);
    }
    
    .login-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(255, 0, 0, 0.1);
        padding: 40px;
        margin: 20px auto;
        max-width: 400px;
        border: 2px solid #ff0000;
    }
    
    .logo-container {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .logo {
        max-width: 200px;
        height: auto;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(255,0,0,0.2);
        display: block;
        margin: 0 auto;
    }
    
    .title {
        color: #ff0000 !important;
        text-align: center !important;
        font-size: 28px !important;
        font-weight: bold !important;
        margin-bottom: 10px !important;
        display: block !important;
    }
    
    .subtitle {
        color: #666 !important;
        text-align: center !important;
        font-size: 16px !important;
        margin-bottom: 30px !important;
        display: block !important;
    }
    
    .form-container {
        background: #fafafa;
        border-radius: 10px;
        padding: 25px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    
    .credentials-box {
        background: #fff3f3;
        border: 1px solid #ffcccc;
        border-radius: 8px;
        padding: 15px;
        margin-top: 20px;
    }
    
    .credentials-title {
        color: #ff0000;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .credential-item {
        color: #666;
        margin: 5px 0;
    }
    
    .footer {
        text-align: center;
        margin-top: 30px;
        color: #999;
        font-size: 12px;
    }
    
    /* Custom styling for Streamlit elements */
    .stTextInput > div > div > input {
        border: 2px solid #e0e0e0 !important;
        border-radius: 6px !important;
        padding: 12px !important;
        font-size: 14px !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff0000 !important;
        box-shadow: 0 0 0 2px rgba(255, 0, 0, 0.1) !important;
    }
    
    .stFormSubmitButton > button {
        background: #ff0000 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: #cc0000 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.3) !important;
    }
    
    /* Style Streamlit markdown headers for login page */
    .stMarkdown h3 {
        color: #ff0000 !important;
        text-align: center !important;
        font-size: 28px !important;
        font-weight: bold !important;
        margin-bottom: 10px !important;
        margin-top: 20px !important;
    }
    
    .stMarkdown em {
        color: #666 !important;
        text-align: center !important;
        font-size: 16px !important;
        margin-bottom: 30px !important;
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Logo path
    logo_path = r"unnamed (2).jpg"
    
    # Convert logo to base64
    logo_base64 = get_image_base64(logo_path)
    
    # Display the header section using Streamlit components
    st.markdown("""
    <div class="login-container">
        <div class="logo-container" style="text-align: center; margin-bottom: 20px;">
    """, unsafe_allow_html=True)
    
    # Display logo using Streamlit with proper centering
    if logo_base64:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{logo_base64}" class="logo" alt="Company Logo" style="display: block; margin: 0 auto;"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: center;"><div style="width: 200px; height: 100px; background: #ff0000; border-radius: 10px; margin: 0 auto; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">NBP</div></div>', unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Use Streamlit components for title and subtitle with proper spacing
    st.markdown("### Welcome to NBP")
    st.markdown("*Sign in to your account*")

def auth_component():
    """Custom authentication component with beautiful login page"""
    
    # Hide default Streamlit elements for login page
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f8f8f8 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create the custom login page
    create_custom_login_page()
    
    # Form container with custom styling
    st.markdown("""
    <div class="form-container">
        <div style="margin-bottom: 15px;">
            <label style="color: #333; font-weight: bold; margin-bottom: 8px; display: block;">Username</label>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", key="login_username", placeholder="Enter your username", label_visibility="collapsed")
        
        st.markdown("""
        <div style="margin-bottom: 15px;">
            <label style="color: #333; font-weight: bold; margin-bottom: 8px; display: block;">Password</label>
        </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password", label_visibility="collapsed")
        
        submit_button = st.form_submit_button("Sign In", use_container_width=True)
    
    # Close form container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Credentials and footer
    st.markdown("""
    <div class="credentials-box">
        <div class="credentials-title">Demo Credentials</div>
        <div class="credential-item">👤 Username: <strong>sales_rep</strong></div>
        <div class="credential-item">🔑 Password: <strong>nbp2025</strong></div>
    </div>
    
    <div class="footer">
        © 2024 NBP. All rights reserved.
    </div>
    """, unsafe_allow_html=True)
    
    if submit_button:
            result = auth.authenticate_user(username, password)
            if result["success"]:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_id = result["user"]["id"]
                st.session_state.user_role = result["user"]["role"]
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("❌ " + result["message"])

def check_authentication():
    """Check if user is authenticated"""
    if not st.session_state.get('authenticated', False):
        auth_component()
        return False
    return True

def get_current_user():
    """Get current authenticated user information"""
    if st.session_state.get('authenticated', False):
        return {
            'id': st.session_state.get('user_id'),
            'username': st.session_state.get('username'),
            'role': st.session_state.get('user_role', 'sales_rep')
        }
    return None

def logout():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.rerun() 
