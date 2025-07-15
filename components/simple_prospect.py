import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from database.models import db
from auth import get_current_user

# Meeting objectives
MEETING_OBJECTIVES = [
    "Initial Discovery Call",
    "Product Demo",
    "Solution Presentation",
    "Contract Negotiation",
    "Follow-up Meeting",
    "Referral Discussion"
]

# Company size options
COMPANY_SIZES = [
    "1-10 employees",
    "11-50 employees",
    "51-200 employees",
    "201-500 employees",
    "501-1000 employees",
    "1000+ employees"
]

# Industry options
INDUSTRIES = [
    "Technology",
    "Healthcare",
    "Finance",
    "Education",
    "Manufacturing",
    "Retail",
    "Real Estate",
    "Consulting",
    "Marketing",
    "Legal",
    "Non-profit",
    "Government",
    "Other"
]

def simple_prospect_component():
    """Simple prospect creation component with enhanced UX"""
    st.markdown("""
    <div class="main-container">
        <h1 style="text-align: center; margin-bottom: 2rem;">➕ New Prospect</h1>
        <p style="text-align: center; color: #666; margin-bottom: 3rem; font-size: 1.1rem;">
            Create a comprehensive prospect profile to generate personalized AI reports
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    if not current_user:
        st.error("User not authenticated")
        return
    
    # Progress indicator
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid rgba(255,0,0,0.1);">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: #ff0000; color: white; width: 40px; height: 40px; border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center; font-weight: bold;">1</div>
            <div>
                <h3 style="margin: 0; color: #333;">Create Prospect Profile</h3>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">Fill in the prospect information below</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("simple_prospect_form", clear_on_submit=True):
        # Company Information Section
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,0,0,0.05) 0%, rgba(255,0,0,0.02) 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; border: 1px solid rgba(255,0,0,0.1);">
            <h3 style="margin: 0 0 1rem 0; color: #ff0000; display: flex; align-items: center; gap: 0.5rem;">
                🏢 Company Information
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "Company Name *",
                placeholder="Enter company name",
                help="Full legal name of the company"
            )
            website = st.text_input(
                "Website",
                placeholder="https://www.company.com",
                help="Company website URL"
            )
            industry = st.selectbox(
                "Industry",
                options=INDUSTRIES,
                help="Primary industry of the company"
            )
        
        with col2:
            company_size = st.selectbox(
                "Company Size",
                options=COMPANY_SIZES,
                help="Number of employees"
            )
            meeting_objective = st.selectbox(
                "Meeting Objective *",
                options=MEETING_OBJECTIVES,
                help="Primary goal of the meeting"
            )
        
        # Primary Contact Section
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,0,0,0.05) 0%, rgba(255,0,0,0.02) 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; border: 1px solid rgba(255,0,0,0.1);">
            <h3 style="margin: 0 0 1rem 0; color: #ff0000; display: flex; align-items: center; gap: 0.5rem;">
                👤 Primary Contact
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            primary_contact_name = st.text_input(
                "Contact Name *",
                placeholder="Full name",
                help="Primary contact's full name"
            )
            primary_title = st.text_input(
                "Job Title",
                placeholder="e.g., CEO, Director, Manager",
                help="Contact's job title"
            )
        
        with col2:
            primary_email = st.text_input(
                "Email *",
                placeholder="contact@company.com",
                help="Primary contact's email address"
            )
            primary_phone = st.text_input(
                "Phone",
                placeholder="+1 (555) 123-4567",
                help="Primary contact's phone number"
            )
        
        # Additional Information Section
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,0,0,0.05) 0%, rgba(255,0,0,0.02) 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; border: 1px solid rgba(255,0,0,0.1);">
            <h3 style="margin: 0 0 1rem 0; color: #ff0000; display: flex; align-items: center; gap: 0.5rem;">
                📝 Additional Information
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        context = st.text_area(
            "Context & Notes",
            placeholder="Enter any additional context, notes, or specific requirements for this prospect...",
            height=120,
            help="Additional information about the prospect or meeting"
        )
        
        # Enhanced submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "💾 Save Prospect & Continue", 
                use_container_width=True,
                help="Create the prospect profile and proceed to AI report generation"
            )
        
        if submitted:
            # Validate required fields
            if not company_name or not meeting_objective or not primary_contact_name or not primary_email:
                st.error("Please fill in all required fields (marked with *)")
                return
            
            try:
                # Create prospect data
                prospect_data = {
                    'company_name': company_name,
                    'website': website,
                    'industry': industry,
                    'company_size': company_size,
                    'meeting_objective': meeting_objective,
                    'context': context
                }
                
                # Save prospect to database
                prospect_id = db.create_prospect(current_user['id'], prospect_data)
                
                # Create primary contact
                contact_data = {
                    'contact_name': primary_contact_name,
                    'title': primary_title,
                    'email': primary_email,
                    'phone': primary_phone,
                    'is_primary': True
                }
                
                db.create_contact(prospect_id, contact_data)
                
                # Success message with enhanced styling
                st.markdown(f"""
                <div class="success-message">
                    <h4>✅ Prospect Created Successfully!</h4>
                    <p><strong>{company_name}</strong> has been added to your prospects.</p>
                    <p><strong>Meeting Objective:</strong> {meeting_objective}</p>
                    <p><strong>Primary Contact:</strong> {primary_contact_name} ({primary_email})</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Store prospect info for AI report generation
                st.session_state.current_prospect = {
                    'id': prospect_id,
                    'company_name': company_name,
                    'industry': industry,
                    'meeting_objective': meeting_objective,
                    'primary_contact': primary_contact_name,
                    'context': context
                }
                
                # Next steps with enhanced design
                st.markdown("""
                <div class="red-bg-text" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                            color: white; padding: 2rem; border-radius: 15px; margin: 2rem 0; 
                            box-shadow: 0 8px 25px rgba(40,167,69,0.3); border: 2px solid #28a745;">
                    <h3 style="margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem; color: white;">
                        🚀 Next Steps
                    </h3>
                    <div style="display: grid; gap: 1rem;">
                        <div style="display: flex; align-items: center; gap: 0.8rem;">
                            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 50%;">1</div>
                            <div style="color: white;"><strong>Generate AI Report:</strong> Go to 'AI Report Generation' to create a personalized NBP report</div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.8rem;">
                            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 50%;">2</div>
                            <div style="color: white;"><strong>Review Prospect:</strong> All prospect information has been saved to the database</div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.8rem;">
                            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 50%;">3</div>
                            <div style="color: white;"><strong>Follow Up:</strong> Use the generated report for your meeting preparation</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Auto-navigate to AI Report Generation
                st.session_state.page = "AI Report Generation"
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error creating prospect: {str(e)}")

def validate_prospect_form(company_name: str, meeting_objective: str, primary_contact_name: str, primary_email: str) -> List[str]:
    """Validate prospect form data"""
    errors = []
    
    if not company_name.strip():
        errors.append("Company name is required")
    
    if not meeting_objective:
        errors.append("Meeting objective is required")
    
    if not primary_contact_name.strip():
        errors.append("Primary contact name is required")
    
    if not primary_email.strip():
        errors.append("Primary contact email is required")
    elif '@' not in primary_email:
        errors.append("Please enter a valid email address")
    
    return errors 