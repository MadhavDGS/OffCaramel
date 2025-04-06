import streamlit as st
import base64
from supabase import create_client
from datetime import datetime
import sqlite3
import hashlib
from pathlib import Path

def get_base64_of_bin_file(bin_file):
    """Convert a binary file to a base64 string."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Must be the first Streamlit command
st.set_page_config(
    page_title="OffCaramel Login",
    page_icon="🌠",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)

# Hide sidebar and other Streamlit components
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Center the main content */
    .main > div {
        max-width: 1000px;
        margin: 0 auto;
        padding: 0;
    }
    
    /* Logo styling */
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .logo-container img {
        width: 200px;
        height: auto;
        margin-bottom: 1rem;
    }
    
    /* Login container styling */
    .login-container {
        background: rgba(255, 192, 203, 0.1);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(255, 192, 203, 0.3);
        backdrop-filter: blur(10px);
        max-width: 500px;
        margin: 2rem auto;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #ff69b4, #ff1493);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 12px 24px;
        width: 100%;
        transition: all 0.3s ease;
        margin: 0.5rem 0;
        font-family: 'Joystix', monospace !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Show logo and title
st.markdown("""
    <div class="logo-container">
        <img src="data:image/png;base64,{}"/>
        <h3 style='color: #ff69b4; margin-bottom: 1rem;'>By While(1) Studios</h3>
    </div>
""".format(get_base64_of_bin_file("/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/logo.png")), unsafe_allow_html=True)

# Supabase configuration
SUPABASE_URL = "https://xahzxcipqkckawzcyzcl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhaHp4Y2lwcWtja2F3emN5emNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2NTY5ODMsImV4cCI6MjA1ODIzMjk4M30.J_ND_Jl3MwrR_Yy0v_YC7WwTGJE5dmlJuZcmhJwUvtY"

# Initialize Supabase client
try:
    supabase = create_client(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )
except Exception as e:
    st.error(f"Failed to initialize Supabase client: {str(e)}")

def set_background(png_file):
    """Set the background image for the Streamlit app."""
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp > header {{
        background-color: transparent !important;
    }}
    .stApp > footer {{
        background-color: transparent !important;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

def get_image_base64(image_path):
    """Get base64 encoded image"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def send_otp(email):
    try:
        # Send OTP via email
        auth_response = supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": None,  # Disable magic links
                "data": {
                    "role": st.session_state.temp_role
                }
            }
        })
        return True, "OTP code sent to your email!"
    except Exception as e:
        return False, f"Error sending OTP: {str(e)}"

def verify_otp(email, otp_code):
    try:
        # Verify the OTP code
        auth_response = supabase.auth.verify_otp({
            "email": email,
            "token": otp_code,
            "type": "email"
        })
        
        if auth_response.user:
            try:
                # Try to get existing profile
                profile_response = supabase.table('profiles').select("*").eq('id', auth_response.user.id).execute()
                
                if not profile_response.data or len(profile_response.data) == 0:
                    # Create new profile if it doesn't exist
                    profile_data = {
                        "id": auth_response.user.id,
                        "email": email,
                        "role": st.session_state.get('temp_role', 'Patient'),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Insert new profile
                    insert_response = supabase.table('profiles').insert(profile_data).execute()
                    if insert_response.data:
                        return True, insert_response.data[0]
                    return False, "Failed to create profile"
                else:
                    # Return existing profile
                    return True, profile_response.data[0]
            except Exception as e:
                return False, f"Profile error: {str(e)}"
        return False, "Invalid OTP code"
    except Exception as e:
        return False, f"Verification error: {str(e)}"

def show_login_page():
    # Custom CSS
    st.markdown("""
        <style>
        @font-face {
            font-family: 'Joystix';
            src: url('/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/joystix.monospace-regular (1).otf') format('opentype');
        }

        /* Global font application */
        * {
            font-family: 'Joystix', monospace !important;
        }

        /* Streamlit specific elements */
        .stMarkdown, 
        .stText, 
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div,
        .stMultiSelect > div > div > div,
        .stSlider > div > div > div,
        .stHeader,
        .stSubheader,
        .stMetricLabel,
        .stMetricValue,
        .stProgress > div > div > div,
        .stChatMessage,
        .stChatInput,
        .stAlert,
        .stInfo,
        .stSuccess,
        .stWarning,
        .stError,
        .stTabs > div > div > div,
        .stTab,
        .stDateInput > div > div > input,
        .stTimeInput > div > div > input,
        .stNumberInput > div > div > input,
        .stFileUploader > div > div,
        .stRadio > div,
        .stCheckbox > div,
        .stExpander > div {
            font-family: 'Joystix', monospace !important;
        }

        .stApp {
            background: linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(0,0,0,0.7));
        }
        
        .login-container {
            background: rgba(255, 192, 203, 0.1);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(255, 192, 203, 0.3);
            backdrop-filter: blur(10px);
            max-width: 500px;
            margin: 0 auto;
            margin-top: 50px;
        }

        .stButton > button {
            background: linear-gradient(45deg, #ff69b4, #ff1493);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 20px;
            width: 100%;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 105, 180, 0.4);
        }

        h1, h2, h3, h4, h5, h6 {
            color: #ff69b4 !important;
            text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
            text-align: center;
        }

        /* Form inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 192, 203, 0.3) !important;
            border-radius: 10px !important;
            color: white !important;
            padding: 10px !important;
        }

        /* Radio buttons */
        .stRadio > label {
            color: white !important;
        }

        .stRadio [data-testid="stMarkdownContainer"] > p {
            color: white !important;
        }

        /* Form labels */
        label, .form-label {
            color: white !important;
            margin-bottom: 5px !important;
        }

        /* Error messages */
        .stAlert {
            background: rgba(255, 105, 180, 0.1) !important;
            border: 1px solid rgba(255, 105, 180, 0.3) !important;
            border-radius: 10px !important;
        }

        /* Success messages */
        .stSuccess {
            background: rgba(0, 255, 127, 0.1) !important;
            border: 1px solid rgba(0, 255, 127, 0.3) !important;
            border-radius: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "login"
    if 'verification_sent' not in st.session_state:
        st.session_state.verification_sent = False
    if 'email' not in st.session_state:
        st.session_state.email = ""

    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔐 Login", key="login_btn", use_container_width=True):
            st.session_state.active_tab = "login"
    with col2:
        if st.button("📝 Register", key="register_btn", use_container_width=True):
            st.session_state.active_tab = "register"
    with col3:
        if st.button("👋 Guest", key="guest_btn", use_container_width=True):
            st.session_state.active_tab = "guest"

    # Show different content based on active tab
    if st.session_state.active_tab in ["login", "register"]:
        st.markdown('<p class="form-label">Choose your role</p>', unsafe_allow_html=True)
        role = st.radio("Select Role", ["Patient", "Doctor"], horizontal=True, label_visibility="collapsed")
        st.session_state.temp_role = role
        
        if not st.session_state.verification_sent:
            email = st.text_input("Email Address", key="email_input", value=st.session_state.email, 
                             label_visibility="collapsed", placeholder="Enter your email")
            # Moved OTP input box here to show it regardless of verification status
            otp_code = st.text_input("OTP Code", label_visibility="collapsed", 
                                   placeholder="Enter 6-digit OTP code")
            
            if role == "Doctor":
                if st.button("Login as Doctor (Test Mode)", use_container_width=True):
                    # Simulate successful login for Doctor
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = "test_doctor_id"  # Simulated user ID
                    st.session_state['role'] = "Doctor"
                    st.session_state['email'] = email
                    st.session_state['full_name'] = "Test Doctor"  # Simulated full name
                    st.switch_page("pages/doctor_dashboard.py")
            
            if st.button("Send OTP Code", use_container_width=True):
                if email:
                    success, message = send_otp(email)
                    if success:
                        st.session_state.verification_sent = True
                        st.session_state.email = email
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter your email")
        else:
            otp_code = st.text_input("OTP Code", label_visibility="collapsed", 
                                   placeholder="Enter 6-digit OTP code")
            
            col1, col2 = st.columns([2,1])
            with col1:
                if st.button("Verify OTP", use_container_width=True):
                    if otp_code:
                        success, result = verify_otp(st.session_state.email, otp_code)
                        if success:
                            st.success(f"Welcome, {st.session_state.email}!")
                            st.session_state['logged_in'] = True
                            st.session_state['user_id'] = result['id']
                            st.session_state['role'] = result['role']
                            st.session_state['email'] = result['email']
                            
                            # Redirect to the appropriate dashboard based on role
                            if result['role'] == "Doctor":
                                st.session_state['full_name'] = result.get('full_name', 'Doctor')  # Assuming full_name is part of the profile
                                st.switch_page("pages/doctor_dashboard.py")
                            else:
                                st.switch_page("pages/main.py")
                        else:
                            st.error(result)
                    else:
                        st.warning("Please enter the OTP code")
            
            with col2:
                if st.button("Resend OTP", use_container_width=True):
                    success, message = send_otp(st.session_state.email)
                    if success:
                        st.success("New OTP code sent!")
                    else:
                        st.error(message)

    elif st.session_state.active_tab == "guest":
        st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <h3 style="color: white;">Quick Access</h3>
                <p style="color: rgba(255,255,255,0.8);">
                    Experience basic features without registration
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state['logged_in'] = True
            st.session_state['email'] = 'guest'
            st.session_state['role'] = 'Patient'
            st.switch_page("pages/main.py")

    st.markdown('</div>', unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        show_login_page()

if __name__ == '__main__':
    main() 