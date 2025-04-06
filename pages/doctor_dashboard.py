import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client
import base64
import time

# Initialize Supabase client
SUPABASE_URL = "https://xahzxcipqkckawzcyzcl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhaHp4Y2lwcWtja2F3emN5emNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2NTY5ODMsImV4cCI6MjA1ODIzMjk4M30.J_ND_Jl3MwrR_Yy0v_YC7WwTGJE5dmlJuZcmhJwUvtY"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_base64_video(video_file):
    """Get base64 encoded video data"""
    with open(video_file, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()

def set_background(video_file):
    """Set the background video for the Streamlit app."""
    try:
        video_base64 = get_base64_video(video_file)
        st.markdown(f"""
            <style>
            .stApp {{
                background: rgba(0,0,0,0.7);
            }}
            .video-background {{
                position: fixed;
                right: 0;
                bottom: 0;
                min-width: 100%;
                min-height: 100%;
                width: auto;
                height: auto;
                z-index: -1;
                object-fit: cover;
            }}
            </style>
            <video autoplay muted class="video-background" onended="this.style.opacity = '1';">
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            </video>
            <script>
                const video = document.querySelector('.video-background');
                video.addEventListener('ended', function() {{
                    video.style.opacity = '1';
                }});
            </script>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error setting background: {str(e)}")

def get_base64_of_bin_file(bin_file):
    """Convert a binary file to a base64 string."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def add_logout_button():
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.switch_page("login.py")

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Doctor's Dashboard | OffCaramel",
        page_icon="��",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add the same CSS styling
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(0,0,0,0.7));
        }
        
        [data-testid="stSidebar"] {
            background-color: rgba(255, 192, 203, 0.2) !important;
            border-right: 1px solid rgba(255, 192, 203, 0.3);
            backdrop-filter: blur(10px);
        }

        .stButton > button {
            background: linear-gradient(45deg, #ff69b4, #ff1493);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 20px;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 105, 180, 0.4);
        }

        .markdown-text-container {
            background: rgba(255, 192, 203, 0.1);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 192, 203, 0.3);
            backdrop-filter: blur(5px);
        }

        /* Add space theme elements */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(255, 192, 203, 0.1) 0%, transparent 20%),
                radial-gradient(circle at 90% 80%, rgba(255, 192, 203, 0.1) 0%, transparent 20%);
            z-index: -1;
        }

        h1, h2, h3 {
            color: #ff69b4 !important;
            text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
        }

        .important-element {
            box-shadow: 0 0 15px rgba(255, 105, 180, 0.3);
        }

        /* Style for metrics */
        .metric-container {
            background: rgba(255, 192, 203, 0.1);
            padding: 15px;
            border-radius: 15px;
            border: 1px solid rgba(255, 192, 203, 0.3);
            backdrop-filter: blur(5px);
            margin: 10px 0;
        }

        /* Style for tables */
        .dataframe {
            background: rgba(255, 192, 203, 0.1) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 192, 203, 0.3) !important;
            backdrop-filter: blur(5px) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check login status and role
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.switch_page("login.py")
    elif st.session_state.get('role') != "Doctor":
        st.error("Unauthorized access")
        st.stop()
    
    # Add logout button
    add_logout_button()
    
    st.title(f"✨ Welcome Dr. {st.session_state.get('full_name', '')}")
    st.markdown("""
        <div class='markdown-text-container'>
        <h3>🌌 OffCaramel By While(1) Studios</h3>
        Your advanced medical dashboard for patient care and analysis.
        </div>
    """, unsafe_allow_html=True)
    
    # Set background video
    background_path = r"/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/editspace (online-video-cutter.com).mp4"
    set_background(background_path)

    # Store doctor's email from session state
    doctor_email = st.session_state.get('email', 'test_doctor@example.com')

    # Sidebar
    st.sidebar.title("Doctor's Dashboard")
    menu = st.sidebar.selectbox(
        "Menu",
        ["Patient Records", "Analysis Results", "Vision AI", "Heart Disease Prediction", 
         "Hospital Analysis", "Download Report", "Settings"]
    )
    
    if menu == "Patient Records":
        st.header("Patient Records")
        
        # Fetch existing patients from Supabase
        response = supabase.table('patients').select('*').execute()
        patients = response.data

        if patients:
            df_patients = pd.DataFrame(patients)
            st.dataframe(df_patients)
            
            # Only show delete functionality if there are patients
            delete_patient_id = st.number_input("Delete Patient ID", min_value=1, max_value=len(patients), step=1)
            if st.button("Delete Patient"):
                if delete_patient_id <= len(patients):
                    patient_id = patients[delete_patient_id - 1]['id']
                    supabase.table('patients').delete().eq('id', patient_id).execute()
                    st.success("Patient deleted successfully!")
                else:
                    st.error("Invalid Patient ID.")
        else:
            st.write("No patient records found.")
            st.warning("You cannot delete a patient because there are no records.")

        # Form to add a new patient
        with st.form("Add Patient"):
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=0)
            condition = st.text_input("Condition")
            last_visit = st.date_input("Last Visit", datetime.today())
            submit_button = st.form_submit_button("Add Patient")
            if submit_button:
                new_patient = {
                    "name": name,
                    "age": age,
                    "condition": condition,
                    "last_visit": last_visit.isoformat()  # Convert date to string
                }
                supabase.table('patients').insert(new_patient).execute()
                st.success("Patient added successfully!")

    elif menu == "Analysis Results":
        st.header("Analysis Results")
        
        # Fetch existing analysis results from Supabase
        response = supabase.table('analysis_results').select('*').execute()
        analysis_results = response.data    

        if analysis_results:
            df_analysis = pd.DataFrame(analysis_results)
            st.dataframe(df_analysis)
            
            # Only show delete functionality if there are results
            delete_test_id = st.number_input("Delete Test ID", min_value=1, max_value=len(analysis_results), step=1)
            if st.button("Delete Analysis Result"):
                if delete_test_id <= len(analysis_results):
                    test_id = analysis_results[delete_test_id - 1]['id']
                    supabase.table('analysis_results').delete().eq('id', test_id).execute()
                    st.success("Analysis result deleted successfully!")
                else:
                    st.error("Invalid Test ID.")
        else:
            st.write("No analysis results found.")
            st.warning("You cannot delete an analysis result because there are no records.")
        
        # Form to add a new analysis result
        with st.form("Add Analysis Result"):
            patient_name = st.text_input("Patient Name")
            test_type = st.text_input("Test Type")
            result = st.selectbox("Result", ["Normal", "Abnormal"])
            test_date = st.date_input("Test Date", datetime.today())
            submit_button = st.form_submit_button("Add Analysis Result")
            if submit_button:
                new_analysis_result = {
                    "patient_name": patient_name,
                    "test_type": test_type,
                    "result": result,
                    "date": test_date.isoformat()
                }
                supabase.table('analysis_results').insert(new_analysis_result).execute()
                st.success("Analysis result added successfully!")

    elif menu == "Vision AI":
        st.switch_page("pages/vision_app.py")

    elif menu == "Heart Disease Prediction":
        st.switch_page("pages/HeartDiseasePrediction.py")

    elif menu == "Hospital Analysis":
        st.header("Hospital Analysis")
        
        # Add hospital analysis metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Total Patients", value="1,234", delta="12%")
            st.metric(label="Average Stay", value="4.5 days", delta="-2%")
            
        with col2:
            st.metric(label="Bed Occupancy", value="78%", delta="5%")
            st.metric(label="Staff Utilization", value="85%", delta="3%")
            
        with col3:
            st.metric(label="Patient Satisfaction", value="4.2/5", delta="0.3")
            st.metric(label="Treatment Success Rate", value="92%", delta="4%")
        
        # Add charts
        st.subheader("Patient Demographics")
        # Add demographic charts here
        
        st.subheader("Treatment Outcomes")
        # Add outcome charts here

    elif menu == "Download Report":
        st.header("Download Reports")
        
        report_type = st.selectbox(
            "Select Report Type",
            ["Patient Summary", "Treatment Outcomes", "Hospital Statistics", "Staff Performance"]
        )
        
        date_range = st.date_input(
            "Select Date Range",
            [datetime.today() - timedelta(days=30), datetime.today()]
        )
        
        format_type = st.radio(
            "Select Format",
            ["PDF", "Excel", "CSV"]
        )
        
        if st.button("Generate Report"):
            with st.spinner("Generating report..."):
                time.sleep(2)  # Simulate report generation
                st.success("Report generated successfully!")
                st.download_button(
                    label="Download Report",
                    data=b"Sample report data",  # Replace with actual report data
                    file_name=f"{report_type}_{date_range[0]}_{date_range[1]}.{format_type.lower()}",
                    mime="application/octet-stream"
                )

    elif menu == "Settings":
        st.header("Settings")
        st.write("Settings functionality can be implemented here.")
        # Placeholder for settings options
        st.text_input("Change Password")
        st.text_input("Update Profile")
        if st.button("Save Changes"):
            st.success("Changes saved successfully!")

if __name__ == "__main__":
    main() 