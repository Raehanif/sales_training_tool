import streamlit as st
import openai
import json
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
from database.models import db
from auth import get_current_user
from dotenv import load_dotenv
from components.pdf_generator import download_pdf_report, test_pdf_generation

# Load environment variables
load_dotenv()

def initialize_openai_client(api_key: str) -> Optional[openai.OpenAI]:
    """Initialize OpenAI client with API key"""
    if not api_key:
        return None
    
    # Method 1: Try with environment variable cleanup and monkey patching
    try:
        import os
        import openai._client
        
        # Temporarily unset any proxy-related environment variables
        original_proxy_vars = {}
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
        
        for var in proxy_vars:
            if var in os.environ:
                original_proxy_vars[var] = os.environ[var]
                del os.environ[var]
        
        # Monkey patch the OpenAI client to ignore proxies argument
        original_init = openai._client.Client.__init__
        
        def patched_init(self, *args, **kwargs):
            # Remove proxies from kwargs if present
            kwargs.pop('proxies', None)
            return original_init(self, *args, **kwargs)
        
        # Apply the patch
        openai._client.Client.__init__ = patched_init
        
        try:
            client = openai.OpenAI(api_key=api_key)
            return client
        finally:
            # Restore original method
            openai._client.Client.__init__ = original_init
            # Restore original environment variables
            for var, value in original_proxy_vars.items():
                os.environ[var] = value
    except Exception as e:
        st.warning(f"Method 1 failed: {str(e)}")
    
    # Method 2: Try with explicit http_client configuration
    try:
        client = openai.OpenAI(
            api_key=api_key,
            http_client=None
        )
        return client
    except Exception as e:
        st.warning(f"Method 2 failed: {str(e)}")
    
    # Method 3: Try with minimal configuration
    try:
        client = openai.OpenAI(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"All initialization methods failed: {str(e)}")
        st.info("💡 Try updating your OpenAI library: pip install --upgrade openai")
        return None

def get_environment_api_key() -> Optional[str]:
    """Get hardcoded OpenAI API key"""
    return "abc"

def check_openai_version() -> bool:
    """Check if OpenAI library version is compatible"""
    try:
        import pkg_resources
        version = pkg_resources.get_distribution("openai").version
        # Check if version is 1.6.0 or higher
        version_parts = version.split('.')
        if len(version_parts) >= 2:
            major = int(version_parts[0])
            minor = int(version_parts[1])
            return major >= 1 and minor >= 6
        return False
    except Exception:
        return False

def create_safe_openai_client(api_key: str) -> Optional[openai.OpenAI]:
    """Create OpenAI client with safe initialization"""
    try:
        import os
        import openai._client
        
        # Store original environment
        original_env = dict(os.environ)
        
        # Remove proxy-related environment variables
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
        for var in proxy_vars:
            os.environ.pop(var, None)
        
        # Create a custom client class that ignores proxies
        class SafeOpenAIClient(openai.OpenAI):
            def __init__(self, *args, **kwargs):
                # Remove any proxy-related arguments
                kwargs.pop('proxies', None)
                kwargs.pop('http_client', None)
                super().__init__(*args, **kwargs)
        
        # Create client using the safe class
        client = SafeOpenAIClient(api_key=api_key)
        
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)
        
        return client
    except Exception as e:
        st.error(f"Safe client creation failed: {str(e)}")
        return None

def test_openai_connection(api_key: str) -> bool:
    """Test OpenAI connection with a simple API call"""
    try:
        client = create_safe_openai_client(api_key)
        if client is None:
            return False
        
        # Make a simple test call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True
    except Exception:
        return False

def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key"""
    if not api_key:
        return False
    
    # Basic validation - check if it starts with 'sk-'
    if not api_key.startswith('sk-'):
        return False
    
    return True

def create_ai_report_prompt(prospect_info: Dict[str, Any]) -> str:
    """Create a comprehensive AI report prompt"""
    
    company_name = prospect_info.get('company_name', 'the prospect')
    industry = prospect_info.get('industry', 'their industry')
    meeting_objective = prospect_info.get('meeting_objective', 'general discussion')
    context = prospect_info.get('context', '')
    primary_contact = prospect_info.get('primary_contact', 'the contact')
    
    prompt = f"""You are an expert sales professional creating a comprehensive meeting preparation report for NBP (National Business Partners).

PROSPECT INFORMATION:
- Company: {company_name}
- Industry: {industry}
- Meeting Objective: {meeting_objective}
- Primary Contact: {primary_contact}
- Additional Context: {context}

REQUIREMENTS:
Create a detailed, professional report that includes:

1. **Executive Summary** (2-3 sentences)
2. **Company Analysis** (industry insights, potential challenges, opportunities)
3. **Meeting Strategy** (specific approach for {meeting_objective})
4. **Key Talking Points** (3-5 main points to discuss)
5. **Value Proposition** (how NBP can help this specific company)
6. **Questions to Ask** (5-7 strategic questions)
7. **Next Steps** (clear action items)
8. **Risk Assessment** (potential objections and responses)

TONE: Professional, consultative, and solution-focused
LENGTH: Comprehensive but concise (500-800 words)
FORMAT: Well-structured with clear sections and bullet points

Make the report specific to {company_name} and their {industry} industry, focusing on the {meeting_objective} objective."""

    return prompt

def generate_ai_report(client: openai.OpenAI, prompt: str) -> Dict[str, Any]:
    """Generate AI report using OpenAI API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert sales consultant and business analyst specializing in B2B sales preparation and strategic meeting planning."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1500,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        generated_report = response.choices[0].message.content
        
        return {
            "success": True,
            "report": generated_report,
            "model_used": "gpt-4o-mini",
            "tokens_used": response.usage.total_tokens if response.usage else 0,
            "generation_time": datetime.now().isoformat()
        }
        
    except openai.AuthenticationError:
        return {"success": False, "error": "Invalid API key. Please check your OpenAI API key."}
    except openai.RateLimitError:
        return {"success": False, "error": "Rate limit exceeded. Please try again in a moment."}
    except openai.APIError as e:
        return {"success": False, "error": f"OpenAI API error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Generation error: {str(e)}"}

def generate_ai_report_safe(api_key: str, prompt: str) -> Dict[str, Any]:
    """Generate AI report using safe client creation"""
    try:
        client = create_safe_openai_client(api_key)
        if client is None:
            return {"success": False, "error": "Failed to create OpenAI client"}
        
        return generate_ai_report(client, prompt)
    except Exception as e:
        return {"success": False, "error": f"Client creation error: {str(e)}"}

def save_report_to_database(report_data: Dict[str, Any], prospect_id: int, user_id: int) -> bool:
    """Save generated report to database"""
    try:
        script_id = db.create_generated_script(
            prospect_id=prospect_id,
            user_id=user_id,
            script_data={
                'script_type': 'AI Report',
                'content': report_data['report'],
                'ai_model': report_data['model_used'],
                'tokens_used': report_data['tokens_used']
            }
        )
        return script_id > 0
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")
        return False

def ai_report_component():
    """Enhanced AI report generation component with modern UX"""
    st.markdown("""
    <div class="main-container">
        <h1 style="text-align: center; margin-bottom: 2rem;">🤖 AI Report Generation</h1>
        <p style="text-align: center; color: #666; margin-bottom: 3rem; font-size: 1.1rem;">
            Generate personalized AI-powered sales reports for your prospects
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    if not current_user:
        st.error("User not authenticated")
        return
    
    # Check if there's a current prospect
    current_prospect = st.session_state.get('current_prospect')
    
    if not current_prospect:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); 
                    color: white; padding: 2rem; border-radius: 15px; margin: 2rem 0; 
                    box-shadow: 0 8px 25px rgba(255,193,7,0.3); border: 2px solid #ffc107;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 2rem;">⚠️</div>
                <div>
                    <h3 style="margin: 0; color: white;">No Prospect Selected</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Please create a prospect first to generate AI reports.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick action button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ Create New Prospect", use_container_width=True, help="Go to prospect creation page"):
                st.session_state.page = "New Prospect"
                st.rerun()
        return
    
    # Display prospect information with enhanced design
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid rgba(255,0,0,0.1);">
        <h3 style="margin: 0 0 1.5rem 0; color: #ff0000; display: flex; align-items: center; gap: 0.5rem;">
            📋 Prospect Information
        </h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(255,0,0,0.05); padding: 1rem; border-radius: 10px; border: 1px solid rgba(255,0,0,0.1);">
            <p style="margin: 0.5rem 0;"><strong>🏢 Company:</strong> {current_prospect['company_name']}</p>
            <p style="margin: 0.5rem 0;"><strong>🏭 Industry:</strong> {current_prospect['industry']}</p>
            <p style="margin: 0.5rem 0;"><strong>👤 Primary Contact:</strong> {current_prospect['primary_contact']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(255,0,0,0.05); padding: 1rem; border-radius: 10px; border: 1px solid rgba(255,0,0,0.1);">
            <p style="margin: 0.5rem 0;"><strong>🎯 Meeting Objective:</strong> {current_prospect['meeting_objective']}</p>
            <p style="margin: 0.5rem 0;"><strong>📝 Context:</strong> {current_prospect.get('context', 'No additional context provided')[:50]}{'...' if len(current_prospect.get('context', '')) > 50 else ''}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>")
    
    st.markdown("---")
    
    # OpenAI Configuration with enhanced design
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid rgba(255,0,0,0.1);">
        <h3 style="margin: 0 0 1.5rem 0; color: #ff0000; display: flex; align-items: center; gap: 0.5rem;">
            🔑 OpenAI Configuration
        </h3>
    """, unsafe_allow_html=True)
    
    # Check OpenAI library version
    if not check_openai_version():
        st.warning("⚠️ OpenAI library version may be outdated")
        st.info("💡 Consider updating: `pip install --upgrade openai`")
    
    # Get hardcoded API key
    api_key = get_environment_api_key()
    
    if api_key:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                    color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="font-size: 1.2rem;">✅</div>
                <div>
                    <strong>API Key Configured</strong>
                    <p style="margin: 0.2rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Ready to generate AI reports</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Test connection button
        col1, col2 = st.columns([3, 1])
        with col1:
            client = create_safe_openai_client(api_key)
        with col2:
            if st.button("🔍 Test Connection", help="Test if the API key works"):
                if test_openai_connection(api_key):
                    st.success("✅ Connection successful!")
                else:
                    st.error("❌ Connection failed. Please check the configuration.")
    else:
        st.error("❌ API key not configured")
        client = None
    
    st.markdown("</div>")
    
    # Generate Report Section with enhanced design
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid rgba(255,0,0,0.1);">
        <h3 style="margin: 0 0 1.5rem 0; color: #ff0000; display: flex; align-items: center; gap: 0.5rem;">
            📄 Generate AI Report
        </h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate AI Report", use_container_width=True, disabled=not client, help="Generate a comprehensive AI report for this prospect"):
            if not client:
                st.error("Please check the OpenAI configuration.")
                return
            
            with st.spinner("🤖 Generating comprehensive AI report..."):
                # Create prompt
                prompt = create_ai_report_prompt(current_prospect)
                
                # Generate report using safe method
                result = generate_ai_report_safe(api_key, prompt)
                
                if result["success"]:
                    # Display the report with enhanced styling
                    st.markdown("""
                    <div class="red-bg-text" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                                color: white; padding: 2rem; border-radius: 15px; margin: 2rem 0; 
                                box-shadow: 0 8px 25px rgba(40,167,69,0.3); border: 2px solid #28a745;">
                        <h3 style="margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem; color: white;">
                            ✅ AI Report Generated Successfully!
                        </h3>
                        <p style="margin: 0; opacity: 0.9; color: white;">Your personalized NBP report is ready for review and download.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Save to database
                    if save_report_to_database(result, current_prospect['id'], current_user['id']):
                        st.success("✅ Report saved to database")
                    
                    # Display report in a modern container
                    st.markdown("""
                    <div style="background: white; padding: 2rem; border-radius: 15px; margin: 2rem 0; 
                                box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid rgba(255,0,0,0.1);">
                        <h3 style="margin: 0 0 1.5rem 0; color: #ff0000;">📋 Generated Report</h3>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(result["report"])
                    
                    st.markdown("</div>")
                    
                    # Report details with enhanced design
                    st.markdown("""
                    <div style="background: rgba(255,0,0,0.05); padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                                border: 1px solid rgba(255,0,0,0.1);">
                        <h4 style="margin: 0 0 1rem 0; color: #ff0000;">📊 Report Details</h4>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px; border: 1px solid rgba(255,0,0,0.1);">
                            <div style="font-size: 1.5rem; color: #ff0000; margin-bottom: 0.5rem;">🤖</div>
                            <div style="font-weight: bold;">Model</div>
                            <div style="color: #666;">{result['model_used']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px; border: 1px solid rgba(255,0,0,0.1);">
                            <div style="font-size: 1.5rem; color: #ff0000; margin-bottom: 0.5rem;">🔢</div>
                            <div style="font-weight: bold;">Tokens Used</div>
                            <div style="color: #666;">{result['tokens_used']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px; border: 1px solid rgba(255,0,0,0.1);">
                            <div style="font-size: 1.5rem; color: #ff0000; margin-bottom: 0.5rem;">⏰</div>
                            <div style="font-weight: bold;">Generated</div>
                            <div style="color: #666;">{result['generation_time'][:19]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>")
                    
                    # Action buttons with enhanced design
                    st.markdown("""
                    <div style="background: white; padding: 2rem; border-radius: 15px; margin: 2rem 0; 
                                box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid rgba(255,0,0,0.1);">
                        <h3 style="margin: 0 0 1.5rem 0; color: #ff0000;">🎯 Actions</h3>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📋 Copy Report", use_container_width=True, help="Copy the report to clipboard"):
                            st.write("📋 Report copied to clipboard!")
                            st.code(result["report"])
                    
                    with col2:
                        # Generate PDF and create download button
                        pdf_bytes, filename = download_pdf_report(result, current_prospect, "ai_report")
                        if pdf_bytes:
                            st.download_button(
                                label="📄 Download PDF Report",
                                data=pdf_bytes,
                                file_name=filename,
                                mime="application/pdf",
                                use_container_width=True,
                                help="Download the report as a PDF file"
                            )
                        else:
                            st.error("❌ Failed to generate PDF")
                    
                    with col3:
                        if st.button("🔄 Generate New Report", use_container_width=True, help="Generate a new report"):
                            st.rerun()
                    
                    st.markdown("</div>")
                    
                    # Next steps with enhanced design
                    st.markdown("""
                    <div class="red-bg-text" style="background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); 
                                color: white; padding: 2rem; border-radius: 15px; margin: 2rem 0; 
                                box-shadow: 0 8px 25px rgba(0,123,255,0.3); border: 2px solid #007bff;">
                        <h3 style="margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem; color: white;">
                            🚀 Next Steps
                        </h3>
                        <div style="display: grid; gap: 1rem;">
                            <div style="display: flex; align-items: center; gap: 0.8rem;">
                                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 50%;">1</div>
                                <div style="color: white;"><strong>Review the report</strong> and customize as needed</div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.8rem;">
                                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 50%;">2</div>
                                <div style="color: white;"><strong>Use the talking points</strong> for your meeting preparation</div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.8rem;">
                                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 50%;">3</div>
                                <div style="color: white;"><strong>Prepare responses</strong> to the suggested questions</div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.8rem;">
                                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 50%;">4</div>
                                <div style="color: white;"><strong>Follow up</strong> with the prospect using the insights provided</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.error(f"❌ Report generation failed: {result['error']}")
    
    st.markdown("</div>")
    
    # Report Templates (if no API key)
    if not client:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; margin: 2rem 0; 
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid rgba(255,0,0,0.1);">
            <h3 style="margin: 0 0 1.5rem 0; color: #ff0000;">📋 Report Templates</h3>
            <div style="background: rgba(255,0,0,0.05); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255,0,0,0.1);">
                <p style="margin: 0; color: #666;">💡 <strong>Note:</strong> Check the OpenAI configuration above to generate personalized AI reports.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Show sample report structure
        st.markdown("### Sample Report Structure")
        st.markdown("""
        **Executive Summary**
        Brief overview of the prospect and meeting objectives.
        
        **Company Analysis**
        Industry insights and potential opportunities.
        
        **Meeting Strategy**
        Specific approach for the meeting objective.
        
        **Key Talking Points**
        - Point 1
        - Point 2
        - Point 3
        
        **Value Proposition**
        How NBP can help this specific company.
        
        **Questions to Ask**
        Strategic questions to engage the prospect.
        
        **Next Steps**
        Clear action items and follow-up plan.
        """)
        
        st.markdown("</div>")
    
    # Test PDF generation
    with st.expander("🧪 Test PDF Generation", expanded=False):
        if st.button("Test PDF Generation", help="Test if PDF generation is working"):
            test_pdf_generation()
    
    # Help section with enhanced design
    with st.expander("💡 How to Use AI Reports", expanded=False):
        st.markdown("""
        <div style="background: rgba(255,0,0,0.05); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255,0,0,0.1);">
            <h4 style="margin: 0 0 1rem 0; color: #ff0000;">📖 Usage Guide</h4>
            <div style="display: grid; gap: 1rem;">
                <div>
                    <strong>1. Review the Report</strong>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">Read through all sections carefully and note the key talking points and questions.</p>
                </div>
                <div>
                    <strong>2. Customize for Your Style</strong>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">Adapt the language to your communication style and add personal insights.</p>
                </div>
                <div>
                    <strong>3. Prepare Your Materials</strong>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">Use the insights to prepare your presentation and have responses ready for objections.</p>
                </div>
                <div>
                    <strong>4. Follow Up</strong>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">Use the next steps as your action plan and track your progress and outcomes.</p>
                </div>
            </div>
        </div>
        """) 
