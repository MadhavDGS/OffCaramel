import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import absl.logging
import os
import base64
absl.logging.set_verbosity(absl.logging.ERROR)

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
            .video-container {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100vh;
                overflow: hidden;
                z-index: -1;
            }}
            .video-background {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                min-width: 100%;
                min-height: 100%;
                width: auto;
                height: auto;
                object-fit: cover;
            }}
            </style>
            <div class="video-container">
                <video autoplay muted loop playsinline class="video-background">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                </video>
            </div>
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

# Update page config
st.set_page_config(
    page_title="Vision AI Analyzer | OffCaramel",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check login status only (remove role check)
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.switch_page("login.py")

# Add logout button
add_logout_button()

# Update background path - use the new video file
background_path = r"/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/editspace.mp4"
set_background(background_path)

# Set your API key
GOOGLE_API_KEY = "AIzaSyBOauDlaYrpmADTFDBnb3l6ybfmEUSpygw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Initialize Google Generative AI client
genai.configure(api_key=GOOGLE_API_KEY)

# Add the same CSS styling
st.markdown("""
    <style>
    @font-face {
        font-family: 'Joystix';
        src: url('/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/joystix.monospace-regular (1).otf') format('opentype');
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
        font-family: 'Joystix', monospace;
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
        font-family: 'Joystix', monospace;
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

    h1, h2, h3, h4, h5, h6 {
        color: #ff69b4 !important;
        text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
        font-family: 'Joystix', monospace !important;
    }

    .important-element {
        box-shadow: 0 0 15px rgba(255, 105, 180, 0.3);
    }

    /* Style for file uploader */
    [data-testid="stFileUploader"] {
        font-family: 'Joystix', monospace !important;
    }

    /* Style for text elements */
    p, span, label, div {
        font-family: 'Joystix', monospace !important;
    }

    /* Style for analysis results */
    .analysis-results {
        background: rgba(255, 192, 203, 0.1);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 192, 203, 0.3);
        backdrop-filter: blur(5px);
        margin: 20px 0;
        font-family: 'Joystix', monospace;
    }

    /* Style for image captions */
    .stImage > div > div > p {
        font-family: 'Joystix', monospace !important;
        color: #ff69b4 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description with better styling
st.title("🌌 Vision AI Analyzer")
st.markdown("""
    <div class='markdown-text-container'>
    <h3>✨ OffCaramel By While(1) Studios</h3>
    This AI-powered tool analyzes medical images and provides detailed insights.
    Upload an image and let our advanced AI assist you!
    </div>
""", unsafe_allow_html=True)

# Create columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    # Fixed prompt (hidden from UI)
    custom_prompt = """the input will be a medical report image read all the values the output should be just the values in a table format and give basic understand of the value like is it in risk or not or is it low or not . but create tables stricty by making these coloumn namesand follow this strict order"""

# Remove col2 content since we're removing the slider

# Rest of your code for image display and analysis
if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Add analyze button
    if st.button("Analyze Image"):
        with st.spinner("Analyzing image..."):
            try:
                # Resize image
                image.thumbnail([640, 640], Image.Resampling.LANCZOS)
                
                # Convert image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format="PNG")
                img_bytes = img_byte_arr.getvalue()
                
                # Create model instance with the new model name
                model = genai.GenerativeModel("gemini-2.0-flash")
                
                # Generate response with fixed temperature for consistent medical analysis
                response = model.generate_content(
                    [custom_prompt, {"mime_type": "image/png", "data": img_bytes}],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1  # Fixed low temperature for consistent medical analysis
                    )
                )
                
                # Display results
                st.markdown("### Analysis Results")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

