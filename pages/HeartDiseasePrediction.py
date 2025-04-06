import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import base64

# Add these functions for consistent styling with other pages
def set_background(video_file):
    """Set the background video for the Streamlit app."""
    video_file = video_file.replace(" ", "%20")  # Handle spaces in file path
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
            <source src="file://{video_file}" type="video/mp4">
        </video>
        <script>
            const video = document.querySelector('.video-background');
            video.addEventListener('ended', function() {{
                const lastFrame = document.createElement('div');
                lastFrame.style.backgroundImage = `url(${{video.currentSrc}})`;
                lastFrame.style.backgroundSize = 'cover';
                lastFrame.style.position = 'fixed';
                lastFrame.style.top = '0';
                lastFrame.style.left = '0';
                lastFrame.style.width = '100%';
                lastFrame.style.height = '100%';
                lastFrame.style.zIndex = '-1';
                document.body.appendChild(lastFrame);
                video.style.display = 'none';
            }});
        </script>
        """, unsafe_allow_html=True)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def add_logout_button():
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.switch_page("login.py")

# Set page configuration
st.set_page_config(
    page_title="Heart Disease Prediction | OffCaramel",
    page_icon="💝",
    layout="wide"
)

# Add CSS styling
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

    .prediction-container {
        background: rgba(255, 192, 203, 0.1);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 192, 203, 0.3);
        backdrop-filter: blur(5px);
        margin: 20px 0;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ff69b4 !important;
        text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
    }

    /* Input fields */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 192, 203, 0.3) !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 10px !important;
    }

    /* Sliders */
    .stSlider > div > div > div {
        background-color: #ff69b4 !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        background: rgba(255, 192, 203, 0.1);
        padding: 10px 20px;
        border-radius: 10px;
        border: 1px solid rgba(255, 192, 203, 0.3);
        color: #ff69b4 !important;
    }

    /* Risk indicators */
    .risk-high {
        color: #ff4444 !important;
        text-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
    }

    .risk-medium {
        color: #ffbb33 !important;
        text-shadow: 0 0 10px rgba(255, 187, 51, 0.5);
    }

    .risk-low {
        color: #00C851 !important;
        text-shadow: 0 0 10px rgba(0, 200, 81, 0.5);
    }

    /* Labels and text */
    label, p, li {
        color: white !important;
    }

    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(45deg, #ff69b4, #ff1493) !important;
    }

    /* Expandable sections */
    .streamlit-expanderHeader {
        color: #ff69b4 !important;
        background: rgba(255, 192, 203, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(255, 192, 203, 0.3);
    }

    /* Tables */
    .dataframe {
        background: rgba(255, 192, 203, 0.1) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 192, 203, 0.3) !important;
    }

    .dataframe th {
        background: rgba(255, 192, 203, 0.2) !important;
        color: #ff69b4 !important;
    }

    .dataframe td {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Check login status
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.switch_page("login.py")

# Add logout button
add_logout_button()

# Set background image
background_path = "/Users/sreemadhav/SreeMadhav/Mhv%20CODES/MahindraUniversity/OffCaramel/editspace%20(online-video-cutter.com).mp4"
set_background(background_path)

# Load dataset for preprocessing reference
df = pd.read_csv(r"/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/heart_attack_dataset_processed.csv")
X = df.drop(columns=["Outcome"])
y = df["Outcome"]

# Define selected features based on the provided dataset
selected_features = [
    "Age", "Gender", "Cholesterol", "BloodPressure", "HeartRate", "BMI",
    "Smoker", "FamilyHistory", "PhysicalActivity", "AlcoholConsumption", "StressLevel"
]

# Standardize only the selected features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X[selected_features])

# Train Logistic Regression model
model = LogisticRegression(C=1, solver='liblinear', max_iter=500, random_state=42)
model.fit(X_scaled, y)

def predict_cardiac_arrest(input_data):
    input_array = np.array(input_data).reshape(1, -1)
    input_scaled = scaler.transform(input_array)
    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0][1]
    return prediction, probability

# Define feature ranges
feature_ranges = {
    "Age": (20, 100),
    "Gender": (0, 1),  # 0 = Female, 1 = Male
    "Cholesterol": (100, 400),
    "BloodPressure": (80, 200),
    "HeartRate": (50, 150),
    "BMI": (15, 40),
    "Smoker": (0, 1),  # 0 = Non-smoker, 1 = Smoker
    "FamilyHistory": (0, 1),  # 0 = No, 1 = Yes
    "PhysicalActivity": (1, 5),  # 1 = Sedentary, 5 = Highly Active
    "AlcoholConsumption": (0, 7),  # 0 = Never, 7 = Daily
    "StressLevel": (1, 10)
}

# Update the UI section with better styling
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <img src="data:image/png;base64,{get_base64_of_bin_file('/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/logo.png')}" 
             style="width: 150px; height: auto; margin-bottom: 1rem;">
    </div>
""", unsafe_allow_html=True)

st.title("💝 Heart Disease Prediction")
st.markdown("""
    <div class='prediction-container'>
    <h3>🌌 OffCaramel By While(1) Studios</h3>
    Advanced AI-powered heart disease prediction system using machine learning algorithms.
    </div>
""", unsafe_allow_html=True)

# Create two columns for inputs
col1, col2 = st.columns(2)

inputs = []
for i, (feature, (min_val, max_val)) in enumerate(feature_ranges.items()):
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"#### {feature}")
        if feature == "Gender":
            value = st.selectbox("Select", options=["Male", "Female"], key=f"select_{feature}")
            value = 1 if value == "Male" else 0
        elif feature == "AlcoholConsumption":
            value = st.selectbox("Times per week", options=list(range(min_val, max_val + 1)), key=f"select_{feature}")
        else:
            value = st.number_input(f"Range: {min_val}-{max_val}", min_value=min_val, max_value=max_val, 
                                  value=(min_val + max_val) // 2, key=f"input_{feature}")
        inputs.append(value)

# Center the predict button
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🔍 Analyze Risk", use_container_width=True):
        prediction, probability = predict_cardiac_arrest(inputs)
        
        # Style the results
        st.markdown("""
            <div class='prediction-container'>
            """, unsafe_allow_html=True)
        
        if prediction == 1:
            st.error(f"⚠️ High Risk Detected\nRisk Probability: {probability:.2%}")
            st.markdown("""
                ### Recommendations:
                - Schedule an appointment with a cardiologist
                - Monitor your blood pressure regularly
                - Consider lifestyle modifications
                """)
        else:
            st.success(f"✅ Low Risk Level\nRisk Probability: {probability:.2%}")
            st.markdown("""
                ### Keep up the good work:
                - Maintain your healthy lifestyle
                - Continue regular check-ups
                - Stay active and eat well
                """)
            
        # Show free treatment information for both cases
        st.markdown("""
            ### Free Treatment Options:
            #### Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PMJAY)
            This flagship health insurance scheme covers a wide range of cardiac procedures and treatments, including 
            surgeries and interventions for various heart conditions. Beneficiaries can avail themselves of free 
            treatment at empaneled hospitals nationwide.
            
            **Useful Links:**
            - [PMJAY Official Website](https://nha.gov.in/PM-JAY)
            - [Free Operations for Children with Congenital Heart Disease](https://nhm.assam.gov.in/schemes/free-operations-for-children-having-congenital-heart-disease)
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Add disclaimer at the bottom
st.markdown("""
    <div style='background-color: rgba(0, 0, 0, 0.5); padding: 10px; border-radius: 5px; margin-top: 20px;'>
    ⚕️ <em>This is a screening tool only. Always consult healthcare professionals for medical advice.</em>
    </div>
    """, unsafe_allow_html=True)
