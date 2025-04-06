import os
import cv2
import streamlit as st
from ultralytics import YOLO
import numpy as np
from PIL import Image
import google.generativeai as genai
import io
import warnings
import absl.logging
import base64
from pathlib import Path
import folium
from streamlit_folium import folium_static
import requests
from geopy.geocoders import Nominatim
from datetime import datetime
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Suppress warnings
warnings.filterwarnings('ignore')
absl.logging.set_verbosity(absl.logging.ERROR)


GOOGLE_API_KEY = "AIzaSyCwbIIjKcU4TKo1a44TyeV7T9iS_UOSuZE"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


detection_types = {
    "brain_tumor": "🧠 Brain Tumor",
    "eye_disease": "👁️ Eye Disease",
    "diabetic_retinopathy": "👁️ Diabetic Retinopathy",
    "eye_diabetic": "👁️ Eye Diabetic Analysis",
    "nail_diabetic": "💅 Nail Diabetic Analysis",
    "tongue_diabetic": "👅 Tongue Diabetic Analysis",
    "ulcer_diabetic": "🦶 Foot Ulcer Diabetic Analysis"
}

genai.configure(api_key=GOOGLE_API_KEY)


st.set_page_config(
    page_title="AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

import base64
from pathlib import Path

# Add this function before your main code
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

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

# Update background path - use the new video file
background_path = r"/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/editspace.mp4"
set_background(background_path)

# Update the CSS styling section
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
    .stExpander > div,
    .stSidebar [data-testid="stSidebarNav"] span {
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
        font-family: 'Joystix', monospace !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.4);
    }

    /* Chat interface styling */
    .stChatMessage {
        background: rgba(255, 192, 203, 0.1) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 192, 203, 0.3) !important;
        backdrop-filter: blur(5px);
        margin: 10px 0;
        padding: 15px;
    }

    .stChatInput {
        background: rgba(255, 192, 203, 0.1) !important;
        border: 1px solid rgba(255, 192, 203, 0.3) !important;
        border-radius: 20px !important;
        color: white !important;
    }

    /* Headers and text */
    h1, h2, h3, h4, h5, h6, p, span, div, label, input, select, textarea {
        font-family: 'Joystix', monospace !important;
    }

    h1, h2, h3 {
        color: #ff69b4 !important;
        text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255, 192, 203, 0.1);
        border-radius: 15px;
        border: 1px solid rgba(255, 192, 203, 0.3);
        padding: 20px;
    }

    /* Metrics and data display */
    [data-testid="stMetricValue"] {
        font-family: 'Joystix', monospace !important;
        color: #ff69b4 !important;
    }

    /* Tables */
    .dataframe {
        font-family: 'Joystix', monospace !important;
    }

    /* Expandable sections */
    .streamlit-expanderHeader {
        font-family: 'Joystix', monospace !important;
        color: #ff69b4 !important;
    }

    /* Radio buttons and checkboxes */
    .stRadio label, .stCheckbox label {
        font-family: 'Joystix', monospace !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-family: 'Joystix', monospace !important;
    }

    /* Alerts and notifications */
    .stAlert > div {
        font-family: 'Joystix', monospace !important;
    }

    /* Sidebar navigation */
    [data-testid="stSidebarNav"] span {
        font-family: 'Joystix', monospace !important;
    }
    </style>
""", unsafe_allow_html=True)

# Update title and branding
st.title("Welcome to OffCaramel By While(1) Studios")
    
# Update sidebar content
with st.sidebar:
    # Add logo at the top of sidebar
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <img src="data:image/png;base64,{get_base64_of_bin_file('/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/logo.png')}" 
                 style="width: 150px; height: auto; margin-bottom: 1rem;">
            <p style="color: #ff69b4; margin: 0;">By While(1) Studios</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Language selector
    st.subheader("🌐 Language")
    languages = {
        'en': '🇺🇸 English',
        'es': '🇪🇸 Español',
        'fr': '🇫🇷 Français',
        'hi': '🇮🇳 हिंदी',
        'ta': '🇮🇳 தமிழ்',
        'zh': '🇨🇳 中文'
    }
    selected_lang = st.selectbox("", options=list(languages.keys()), 
                                format_func=lambda x: languages[x],
                                key='language')

    # Quick Start Guide section
    st.markdown("---")
    st.subheader("✨ Quick Start Guide")
    st.markdown("""
    #### 1. Medical Image Analysis
    - **📸 Using Camera**
        - Select Camera tab
        - Allow camera access
        - Take a clear photo
        - Choose detection model
        - Click "Analyze"
    
    - **📁 Upload Image**
        - Select Upload tab
        - Choose medical image
        - Select detection model
        - Click "Analyze"
    
    #### 2. AI Detection Models
    - 🧠 Brain Tumor Analysis
    - 👁️ Eye Disease Detection
    - 👁️ Diabetic Retinopathy
    - 👁️ Eye Diabetic Analysis
    - 💅 Nail Diabetic Analysis
    - 👅 Tongue Diabetic Analysis
    - 🦶 Foot Ulcer Diabetic Analysis
    
    #### 3. Key Features
    - **🎯 Real-Time Analysis**
        - Instant AI detection
        - High accuracy results
        - Visual indicators
    
    - **🤖 AI Assistant**
        - Medical guidance
        - Health recommendations
        - Multiple languages
    
    #### 4. Additional Tools
    - 🏥 Hospital Locator
    - 📋 Report Generator
    - 🚨 Emergency Contacts
    
    #### 5. Best Practices
    - Use well-lit environment
    - Keep device steady
    - Follow instructions
    - Wait for processing
    
    #### ⚠️ Important
    This is an AI tool for initial screening only.
    Always consult healthcare professionals.
    
    #### 📞 Support
    - **Email**: support@offcaramel.com
    - **Emergency**: 108
    - **Hospital**: +91-40-66660376
    """)

def load_model(model_type):
    """Load YOLO model based on type"""
    model_paths = {
        'brain_tumor': "braintumorp1.pt",  # your existing model
        'eye_disease': "eye.pt",  # to be added later
        'lung_cancer': "lung_cancer.pt",  # to be added later
        'bone_fracture': "bone.pt",  # to be added later
        'skin_disease': "skin345.pt",  # to be added later
        'diabetic_retinopathy': "xiaoru.pt",
        'eye_diabetic': "eyediabetic.pt",  # Added new model path
        'ulcer': "ulcer.pt",
        'tongue': "tongue(2).pt",
        'nails': "nails.pt"
    }

    if model_type not in st.session_state.models:
        model_path = model_paths.get(model_type)
        if model_path and os.path.exists(model_path):
            st.session_state.models[model_type] = YOLO(model_path)
        else:
            st.warning(f"Model for {model_type} not found. Only Brain Tumor and Diabetic Retinopathy detection are currently available.")
            if model_type not in ['brain_tumor', 'diabetic_retinopathy']:
                return None
            # Fallback to brain tumor model
            st.session_state.models[model_type] = YOLO("braintumorp1.pt")
    return st.session_state.models.get(model_type)


def translate_text(text, target_lang):
    """Translate text to target language"""
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails


def text_to_speech(text, language='en'):
    """Convert text to speech"""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def speech_to_text():
    """Convert speech to text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            return None


def get_gemini_response(prompt, image=None):
    """Get response from Gemini API"""
    try:
        if image:
            # For image analysis, use a specialized medical prompt
            medical_prompt = """
            You are a specialized medical AI assistant focusing on the following conditions:

            1. Brain-related:
               - Brain tumors and related conditions
               - Provide clear indicators and severity levels

            2. Eye-related:
               - General eye diseases
               - Diabetic retinopathy
               - Eye diabetic conditions
               - Focus on early warning signs

            3. Diabetes-related conditions:
               - Nail changes due to diabetes
               - Tongue manifestations of diabetes
               - Diabetic foot ulcers
               - Early detection signs

            Please analyze the image and provide:
            1. Primary condition detected
            2. Confidence level in detection
            3. Key visual indicators observed
            4. Recommended next steps
            5. Urgency level (Low/Medium/High)

            Keep responses concise and clear. Always recommend professional medical consultation.
            Format your response in a structured, easy-to-read manner.
            """
            
            # Combine the user's prompt with our medical prompt
            combined_prompt = f"{medical_prompt}\n\nUser's specific query: {prompt}"
            response = GEMINI_MODEL.generate_content([combined_prompt, image])
        else:
            # For text chat, use the same model
            response = GEMINI_MODEL.generate_content(prompt)

        if hasattr(response, 'text') and response.text:
            return response.text
        return "I apologize, but I couldn't generate a response."

    except Exception as e:
        st.error(f"Error getting AI response: {str(e)}")
        return "I apologize, but I'm having trouble generating a response right now."


def process_chat_response(prompt):
    """Process chat responses with streaming"""
    try:
        response = GEMINI_MODEL.send_message(prompt, stream=True)

        # Create a placeholder for streaming response
        message_placeholder = st.empty()
        full_response = ""

        # Stream the response
        for chunk in response:
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")

        # Replace the placeholder with the complete response
        message_placeholder.markdown(full_response)
        return full_response
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "I apologize, but I'm having trouble generating a response right now."


def analyze_image_with_google_vision(image):
    """Analyze the image using Google Vision API."""
    image = vision.Image(content=image)
    response = vision_client.label_detection(image=image)
    labels = response.label_annotations
    results = [(label.description, label.score) for label in labels]
    return results


def process_image(image):
    """Process the uploaded image and return analysis results."""
    try:
        # Ensure the image is in a valid format
        if isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Analyze the image using Google Vision API
        analysis_results = analyze_image_with_google_vision(img_byte_arr)
        return analysis_results
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None  # Return None if there's an error


def display_prediction(class_name, conf):
    """Legacy function maintained for compatibility"""
    return f"""
    <div style="
        background-color: rgba(0, 0, 0, 0.5);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid rgba(0, 210, 255, 0.3);
    ">
        <h4 style="color: #00d2ff; margin: 0 0 10px 0;">{class_name}</h4>
        <div style="
            background-color: rgba(0, 210, 255, 0.2);
            height: 25px;
            border-radius: 5px;
            position: relative;
            width: 100%;
        ">
            <div style="
                background-color: #00d2ff;
                width: {conf * 100}%;
                height: 100%;
                border-radius: 5px;
            "></div>
            <p style="
                color: white;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                margin: 0;
            ">Confidence: {conf:.2%}</p>
        </div>
    </div>
    """


def initialize_chat_if_needed():
    """Initialize or get existing chat session"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'gemini_chat' not in st.session_state and GEMINI_MODEL:
        st.session_state.gemini_chat = GEMINI_MODEL.start_chat(history=[])


def get_chat_response(prompt):
    """Get chat response from Gemini"""
    try:
        if not GEMINI_MODEL:
            return "AI model not initialized properly. Please check your API key."

        medical_prompt = f"""
        You are a medical AI assistant. Please provide helpful medical information and advice while keeping in mind:
        1. Be clear and professional
        2. Include relevant medical terminology with explanations
        3. Always encourage consulting healthcare professionals
        4. Provide evidence-based information when possible

        User question: {prompt}
        """

        # Generate response (removed creativity settings)
        response = GEMINI_MODEL.generate_content(medical_prompt)

        # Check if response is blocked
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            return "I apologize, but I cannot provide a response to that query. Please try rephrasing your question."

        if hasattr(response, 'text') and response.text:
            return response.text.strip()  # Trim the response

        return "I apologize, but I couldn't generate a response."

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "I apologize, but I'm having trouble generating a response."


def chat_interface(selected_lang):
    """Render chat interface"""
    st.subheader(translate_interface_text("💬 Medical Assistant Chat", selected_lang))

    # Chat input at the top
    if prompt := st.chat_input(translate_interface_text("Ask me anything about your health...", selected_lang)):
        # Add user message
        with st.chat_message("user"):
            st.markdown(translate_interface_text(prompt, selected_lang))
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner(translate_interface_text("Thinking...", selected_lang)):
                response = get_chat_response(prompt)
                # Translate response if needed
                if selected_lang != 'en':
                    response = translate_text(response, selected_lang)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            content = translate_text(message["content"], selected_lang) if selected_lang != 'en' else message["content"]
            st.markdown(content)

    # Add chat guidelines in expandable section at the bottom
    with st.expander(translate_interface_text("ℹ️ Chat Guidelines", selected_lang), expanded=False):
        guidelines = [
            "Ask about medical conditions",
            "Get general health advice",
            "Learn about prevention",
            "Understand detection results"
        ]
        for guideline in guidelines:
            st.markdown(f"- {translate_interface_text(guideline, selected_lang)}")

        st.markdown(f"**{translate_interface_text('Note:', selected_lang)}** " +
                    translate_interface_text(
                        "This is an AI assistant and not a replacement for professional medical advice.",
                        selected_lang))

    # Clear chat button at the bottom
    if st.session_state.chat_history:
        if st.button(translate_interface_text("🗑️ Clear Chat History", selected_lang), key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


def translate_interface_text(text, target_lang):
    """Translate interface text if not in English"""
    if target_lang != 'en':
        try:
            translator = GoogleTranslator(source='en', target=target_lang)
            return translator.translate(text)
        except Exception as e:
            st.error(f"Translation error: {str(e)}")
    return text


def translate_page_content(selected_lang):
    """Translate all static page content"""
    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Initialize img_file variable
        img_file = None

        # Translate tab labels
        tab_labels = [
            translate_interface_text(x, selected_lang)
            for x in ["📸 Camera", "📁 Upload"]
        ]
        tab1, tab2 = st.tabs(tab_labels)

        with tab1:
            # Use session state for language
            camera_label = translate_interface_text("Take a picture", st.session_state.current_language)
            
            # Add custom CSS to force landscape orientation
            st.markdown("""
                <style>
                .stCamera > video {
                    width: 100%;
                    aspect-ratio: 16/9 !important;
                }
                .stCamera > img {
                    width: 100%;
                    aspect-ratio: 16/9 !important;
                    object-fit: cover;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Camera input with custom styling
            img_file_camera = st.camera_input(
                camera_label,
                key="camera_input",
                help="Please capture the image in landscape orientation"
            )
            
            if img_file_camera:
                try:
                    # Read the image from camera
                    image = Image.open(img_file_camera)
                    
                    # Ensure landscape orientation
                    if image.height > image.width:
                        # Rotate the image if it's in portrait
                        image = image.rotate(90, expand=True)
                    
                    # Display captured image with consistent aspect ratio
                    st.image(
                        image, 
                        caption=translate_interface_text("Captured Image", st.session_state.current_language),
                        use_container_width=True
                    )
                    
                    # Generate description using the original image
                    description = generate_image_description(image)
                    st.markdown(f"<h1 style='color: #00d2ff;'>{description}</h1>", unsafe_allow_html=True)

                    # Model selection based on the description
                    select_model_text = translate_interface_text("Select Model for Further Analysis", 
                                                              st.session_state.current_language)
                    selected_model = st.selectbox(
                        select_model_text, 
                        list(detection_types.keys()),
                        key="camera_model_select"
                    )
                    
                    analyze_button_text = translate_interface_text("Analyze Prediction", 
                                                                st.session_state.current_language)
                    if st.button(analyze_button_text, key="camera_analyze_button"):
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_bytes = img_byte_arr.getvalue()
                        
                        analyzed_image = analyze_with_model(selected_model, img_bytes)
                        if analyzed_image is not None:
                            st.image(
                                analyzed_image, 
                                caption=translate_interface_text("Analyzed Image", st.session_state.current_language),
                                use_container_width=True
                            )
                            
                            # Show tabs for different sections
                            result_tabs = st.tabs(["Analysis Results", "Nearby Hospitals", "Download Report"])
                            
                            with result_tabs[0]:
                                # Your existing analysis results code
                                pass
                            
                            with result_tabs[1]:
                                show_hospital_info(description)  # Pass the diagnosis
                            
                            with result_tabs[2]:
                                show_report_section(
                                    diagnosis=description,
                                    confidence=best_detection[1] if 'best_detection' in locals() else 0.0,
                                    image=analyzed_image
                                )

                except Exception as e:
                    st.error(f"Error processing camera image: {str(e)}")

        with tab2:
            uploaded_file = st.file_uploader("Upload a medical image (X-ray, MRI, CT, etc.)", type=["jpg", "png", "jpeg"])
            if uploaded_file:
                try:
                    # Read the file content first
                    file_bytes = uploaded_file.read()
                    
                    # Create PIL Image from bytes
                    image = Image.open(io.BytesIO(file_bytes))
                    
                    # Display the image
                    st.image(image, caption="Uploaded Image", use_container_width=True)
                    
                    # Generate description using the original image
                    description = generate_image_description(image)
                    st.markdown(f"<h1 style='color: #00d2ff;'>{description}</h1>", unsafe_allow_html=True)

                    # Model selection based on the description
                    selected_model = st.selectbox("Select Model for Further Analysis", list(detection_types.keys()))
                    if st.button("Analyze Prediction"):
                        # Create a new bytes buffer for analysis
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_bytes = img_byte_arr.getvalue()
                        
                        # Analyze the prediction based on the selected model
                        analyzed_image = analyze_with_model(selected_model, img_bytes)
                        if analyzed_image is not None:
                            st.image(analyzed_image, caption="Analyzed Image", use_container_width=True)

                    # Add after image analysis in both camera and upload tabs
                    show_hospital_info(description)
                    show_report_section(description, 0.95, image)

                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")

        # Process image if available
        if img_file:
            image = Image.open(img_file)
            st.image(image, caption=translate_interface_text("Uploaded Image", selected_lang), use_container_width=True)

            check_button = st.button(
                translate_interface_text("🔍 Check for Detection", selected_lang),
                key="check_detection_button",
                use_container_width=True
            )

            if check_button:
                process_detection(image, selected_lang)

    # Chat interface in second column
    with col2:
        # Create two columns for the header
        header_col1, header_col2 = st.columns([1, 1])
        
        with header_col1:
            st.markdown("## AI Chat Assistant")
        
        with header_col2:
            st.image("/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/download.gif", 
                    use_container_width=True)

        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)

        # Display chat messages
        for message in st.session_state.get('chat_history', []):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your health..."):
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_chat_response(prompt)
                    st.markdown(response)

        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")


def generate_image_description(image_data):
    """Generate a concise description for the given image using Google Generative AI."""
    try:
        # If image_data is already bytes, convert it to PIL Image
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, Image.Image):
            image = image_data
        else:
            raise ValueError("Unsupported image format")

        # Resize image if needed
        image.thumbnail([640, 640], Image.Resampling.LANCZOS)

        # Convert to bytes for API processing
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_bytes = img_byte_arr.getvalue()

        # Create model instance and generate description
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Updated prompt for more specific detection types
        prompt = """
        Analyze this medical image and provide a concise 7-word response following this format:
        'Detected: [condition]. Use [specific_model] detection.'

        Focus on these specific conditions and their corresponding models:
        1. Brain tumor -> brain tumor detection
        2. Eye disease -> eye disease detection
        3. Diabetic retinopathy -> diabetic retinopathy detection
        4. Eye diabetic condition -> eye diabetic detection
        5. Nail diabetic signs -> nail diabetic detection
        6. Tongue diabetic indicators -> tongue diabetic detection
        7. Foot ulcer diabetic symptoms -> ulcer diabetic detection

        Example responses:
        'Detected: Diabetic retinopathy. Use eye diabetic detection.'
        'Detected: Diabetic nail changes. Use nail diabetic detection.'
        'Detected: Diabetic tongue lesions. Use tongue diabetic detection.'
        'Detected: Diabetic foot ulcer. Use ulcer diabetic detection.'
        """
        
        response = model.generate_content(
            [prompt, {"mime_type": "image/png", "data": img_bytes}],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=30,
                top_p=0.1,
            )
        )

        # Get the response and ensure it's concise
        result = response.text.strip()
        
        # If response is too long, truncate it
        words = result.split()
        if len(words) > 7:
            result = ' '.join(words[:7])

        return result

    except Exception as e:
        st.error(f"Error generating image description: {str(e)}")
        return "Unable to analyze image. Please try again."


def get_current_location():
    """Get user's current location using IP address"""
    try:
        # Get current user's IP
        current_ip_response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if current_ip_response.status_code != 200:
            st.warning("Could not verify your IP address")
            return {'lat': 17.4065, 'lon': 78.4772, 'city': 'Hyderabad'}
        
        current_ip = current_ip_response.json().get('ip', '')
        allowed_ip = "1106.221.177.13"  # Your specific IP
        
        # Check if current IP matches allowed IP
        if current_ip != allowed_ip:
            st.warning("Location services are restricted to authorized IP addresses only.")
            return {'lat': 17.4065, 'lon': 78.4772, 'city': 'Hyderabad'}
        
        # Proceed with location lookup for authorized IP
        response = requests.get(f'https://ipapi.co/{allowed_ip}/json/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Check if we got rate limited
            if data.get('error') and 'rate limit' in data.get('reason', '').lower():
                # Fallback to alternative IP geolocation service
                response = requests.get('https://ipinfo.io/json', timeout=5)
                data = response.json()
            
            # Extract location data with validation
            try:
                coords = data.get('loc', '17.4065,78.4772').split(',')
                location_data = {
                    'lat': float(coords[0]),
                    'lon': float(coords[1]),
                    'city': data.get('city', 'Hyderabad')
                }
                st.success(f"Location found: {location_data['city']}")
                return location_data
            except (IndexError, ValueError):
                st.warning("Could not parse location coordinates. Using default location.")
                return {'lat': 17.4065, 'lon': 78.4772, 'city': 'Hyderabad'}
                
        else:
            st.warning(f"Location service returned status code: {response.status_code}")
            return {'lat': 17.4065, 'lon': 78.4772, 'city': 'Hyderabad'}
            
    except requests.RequestException as e:
        st.warning(f"Network error while fetching location: {str(e)}")
        return {'lat': 17.4065, 'lon': 78.4772, 'city': 'Hyderabad'}
    except Exception as e:
        st.warning(f"Unexpected error getting location: {str(e)}")
        return {'lat': 17.4065, 'lon': 78.4772, 'city': 'Hyderabad'}

def find_nearby_hospitals(lat, lon, radius=5000):
    """Find nearby hospitals using OpenStreetMap"""
    try:
        # Using Overpass API to get hospitals
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius},{lat},{lon});
          way["amenity"="hospital"](around:{radius},{lat},{lon});
          relation["amenity"="hospital"](around:{radius},{lat},{lon});
        );
        out center;
        """
        response = requests.post(overpass_url, data=query)
        data = response.json()
        
        hospitals = []
        for element in data['elements']:
            if 'center' in element:
                lat = element['center']['lat']
                lon = element['center']['lon']
            else:
                lat = element.get('lat', 0)
                lon = element.get('lon', 0)
            
            name = element.get('tags', {}).get('name', 'Unknown Hospital')
            hospitals.append({
                'name': name,
                'lat': lat,
                'lon': lon
            })
        
        return hospitals
    except Exception as e:
        st.error(f"Error finding hospitals: {str(e)}")
        return []

def show_emergency_contacts():
    """Display emergency contacts"""
    st.markdown("""
    ### 🚨 Emergency Contacts
    - **Ambulance**: 108
    - **Police**: 100
    - **Fire**: 101
    - **National Emergency**: 112
    - **Caramel Hospital**: +91-40-66660376
    """)

def create_medical_report(diagnosis, confidence, recommendations):
    """Generate a medical report"""
    now = datetime.now()
    report = {
        "date": now.strftime("%Y-%m-%d %H:%M:%S"),
        "diagnosis": diagnosis,
        "confidence": f"{confidence:.2%}",
        "recommendations": recommendations,
        "disclaimer": "This is an AI-generated report for preliminary analysis only. Please consult a healthcare professional."
    }
    return report

def download_report(report):
    """Create a downloadable report"""
    report_md = f"""
    # AI Medical Analysis Report
    
    **Date**: {report['date']}
    
    ## Diagnosis
    {report['diagnosis']}
    
    ## Confidence Level
    {report['confidence']}
    
    ## Recommendations
    {report['recommendations']}
    
    ## Disclaimer
    {report['disclaimer']}
    """
    return report_md

def analyze_with_model(selected_model, image_data):
    """Simple prediction function following strict pattern"""
    try:
        # Define model paths
        model_paths = {
            "brain_tumor": "brain123.pt",
            "eye_disease": "eye.pt",
            'diabetic_retinopathy': "diabetic.pt",
            'eye_diabetic': "eyediabetic.pt",
            'nail_diabetic': "nails.pt",
            'tongue_diabetic': "tongue(2).pt",
            'ulcer_diabetic': "ulcer.pt"
        }

        # Convert image data to numpy array
        if isinstance(image_data, bytes):
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_data, Image.Image):
            image = np.array(image_data)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif isinstance(image_data, np.ndarray):
            image = image_data
        else:
            raise ValueError("Unsupported image format")

        # Load the model
        model = YOLO(model_paths[selected_model])

        # Run inference with the numpy array
        results = model(image)

        # Process results and save without labels
        for result in results:
            img = result.plot(labels=False)  # Draw results without labels
            
            # For Streamlit display, convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Display result image
            st.image(img_rgb, caption="Detection Result")

            # Display detection information in separate widgets
            if len(result.boxes) > 0:
                # Get all detections
                detections = []
                for box in result.boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = model.names[cls]
                    detections.append((class_name, conf))
                
                # Sort by confidence and get the highest confidence detection
                detections.sort(key=lambda x: x[1], reverse=True)
                best_detection = detections[0]
                
                # Count unique classes
                unique_classes = len(set(d[0] for d in detections))
                
                # Create columns for display
                col1, col2 = st.columns(2)
                
                # Display class information
                with col1:
                    st.metric(
                        label=f"Detected Diseases (Total: {unique_classes})",
                        value=best_detection[0],  # Show highest confidence class
                        delta=f"{len(detections)} Detection(s)"
                    )
                
                # Display confidence for the highest confidence detection
                with col2:
                    st.metric(
                        label="Highest Confidence Score",
                        value=f"{best_detection[1]:.2%}",
                        delta="Confidence Level"
                    )
                    st.progress(best_detection[1])
                
                # If there are multiple detections, show a summary
                if len(detections) > 1:
                    with st.expander("View All Detections"):
                        for class_name, conf in detections:
                            st.text(f"{class_name}: {conf:.2%}")
            else:
                st.warning("No detections found")

            return img_rgb

    except Exception as e:
        st.error(f"Error in prediction: {str(e)}")
        return None

# Add this at the beginning of main.py, after imports
def add_logout_button():
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.switch_page("login.py")

def main():
    # Initialize session state variables
    if 'current_language' not in st.session_state:
        st.session_state.current_language = 'en'  # Default to English
    
    # Check login status and role
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.switch_page("login.py")
    elif st.session_state.get('role') != "Patient":
        st.error("Unauthorized access")
        st.stop()
    
    # Add logout button
    add_logout_button()
    
    # Initialize models dictionary if not exists
    if 'models' not in st.session_state:
        st.session_state.models = {}
    
    # Initialize chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Main content area
    st.markdown("## Medical Image Analysis")
    col1, col2 = st.columns([5, 3])

    with col1:
        # Input method tabs
        tab1, tab2 = st.tabs(["📸 Camera", "📁 Upload"])

        with tab1:
            # Use session state for language
            camera_label = translate_interface_text("Take a picture", st.session_state.current_language)
            
            # Add custom CSS to force landscape orientation
            st.markdown("""
                <style>
                .stCamera > video {
                    width: 100%;
                    aspect-ratio: 16/9 !important;
                }
                .stCamera > img {
                    width: 100%;
                    aspect-ratio: 16/9 !important;
                    object-fit: cover;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Camera input with custom styling
            img_file_camera = st.camera_input(
                camera_label,
                key="camera_input",
                help="Please capture the image in landscape orientation"
            )
            
            if img_file_camera:
                try:
                    # Read the image from camera
                    image = Image.open(img_file_camera)
                    
                    # Ensure landscape orientation
                    if image.height > image.width:
                        # Rotate the image if it's in portrait
                        image = image.rotate(90, expand=True)
                    
                    # Display captured image with consistent aspect ratio
                    st.image(
                        image, 
                        caption=translate_interface_text("Captured Image", st.session_state.current_language),
                        use_container_width=True
                    )
                    
                    # Generate description using the original image
                    description = generate_image_description(image)
                    st.markdown(f"<h1 style='color: #00d2ff;'>{description}</h1>", unsafe_allow_html=True)

                    # Model selection based on the description
                    select_model_text = translate_interface_text("Select Model for Further Analysis", 
                                                              st.session_state.current_language)
                    selected_model = st.selectbox(
                        select_model_text, 
                        list(detection_types.keys()),
                        key="camera_model_select"
                    )
                    
                    analyze_button_text = translate_interface_text("Analyze Prediction", 
                                                                st.session_state.current_language)
                    if st.button(analyze_button_text, key="camera_analyze_button"):
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_bytes = img_byte_arr.getvalue()
                        
                        analyzed_image = analyze_with_model(selected_model, img_bytes)
                        if analyzed_image is not None:
                            st.image(
                                analyzed_image, 
                                caption=translate_interface_text("Analyzed Image", st.session_state.current_language),
                                use_container_width=True
                            )
                            
                            # Show tabs for different sections
                            result_tabs = st.tabs(["Analysis Results", "Nearby Hospitals", "Download Report"])
                            
                            with result_tabs[0]:
                                # Your existing analysis results code
                                pass
                            
                            with result_tabs[1]:
                                show_hospital_info(description)  # Pass the diagnosis
                            
                            with result_tabs[2]:
                                show_report_section(
                                    diagnosis=description,
                                    confidence=best_detection[1] if 'best_detection' in locals() else 0.0,
                                    image=analyzed_image
                                )

                except Exception as e:
                    st.error(f"Error processing camera image: {str(e)}")

        with tab2:
            uploaded_file = st.file_uploader("Upload a medical image (X-ray, MRI, CT, etc.)", type=["jpg", "png", "jpeg"])
            if uploaded_file:
                try:
                    # Read the file content first
                    file_bytes = uploaded_file.read()
                    
                    # Create PIL Image from bytes
                    image = Image.open(io.BytesIO(file_bytes))
                    
                    # Display the image
                    st.image(image, caption="Uploaded Image", use_container_width=True)
                    
                    # Generate description using the original image
                    description = generate_image_description(image)
                    st.markdown(f"<h1 style='color: #00d2ff;'>{description}</h1>", unsafe_allow_html=True)

                    # Model selection based on the description
                    selected_model = st.selectbox("Select Model for Further Analysis", list(detection_types.keys()))
                    if st.button("Analyze Prediction"):
                        # Create a new bytes buffer for analysis
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_bytes = img_byte_arr.getvalue()
                        
                        # Analyze the prediction based on the selected model
                        analyzed_image = analyze_with_model(selected_model, img_bytes)
                        if analyzed_image is not None:
                            st.image(analyzed_image, caption="Analyzed Image", use_container_width=True)

                    # Add after image analysis in both camera and upload tabs
                    show_hospital_info(description)
                    show_report_section(description, 0.95, image)

                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")

    with col2:
        # Create two columns for the header
        header_col1, header_col2 = st.columns([1, 1])
        
        with header_col1:
            st.markdown("## AI Chat Assistant")
        
        with header_col2:
            st.image("/Users/sreemadhav/SreeMadhav/Mhv CODES/MahindraUniversity/OffCaramel/download.gif", 
                    use_container_width=True)

        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)

        # Display chat messages
        for message in st.session_state.get('chat_history', []):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your health..."):
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_chat_response(prompt)
                    st.markdown(response)

        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")


def show_hospital_info(diagnosis):
    st.markdown("### 🏥 Nearby Hospitals")
    
    # Get current location
    location = get_current_location()
    
    # Create map centered on user's location
    m = folium.Map(
        location=[location['lat'], location['lon']], 
        zoom_start=12
    )
    
    # Add user's location marker
    folium.Marker(
        [location['lat'], location['lon']],
        popup='Your Location',
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Find and add nearby hospitals
    hospitals = find_nearby_hospitals(location['lat'], location['lon'])
    for hospital in hospitals:
        folium.Marker(
            [hospital['lat'], hospital['lon']],
            popup=hospital['name'],
            icon=folium.Icon(color='green', icon='plus')
        ).add_to(m)
    
    # Display map
    st.markdown("#### Hospitals Near You")
    folium_static(m)
    
    # Show emergency contacts
    show_emergency_contacts()


def create_pdf_report(report_data, image=None):
    """Create a PDF report using reportlab"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom style for headers
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )

    # Add hospital logo or header
    story.append(Paragraph("Medical Analysis Report", header_style))
    story.append(Spacer(1, 12))

    # Add date
    story.append(Paragraph(f"<b>Date:</b> {report_data['date']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Add diagnosis
    story.append(Paragraph(f"<b>Diagnosis:</b> {report_data['diagnosis']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Add confidence score
    story.append(Paragraph(f"<b>Confidence Score:</b> {report_data['confidence']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Add recommendations
    story.append(Paragraph("<b>Recommendations:</b>", styles["Normal"]))
    for rec in report_data['recommendations']:
        story.append(Paragraph(f"• {rec}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Add the analyzed image if available
    if image is not None:
        # Convert numpy array to PIL Image if necessary
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Save image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Add image to PDF
        img = RLImage(img_byte_arr, width=6*inch, height=4*inch)
        story.append(img)
        story.append(Spacer(1, 12))

    # Add disclaimer
    story.append(Paragraph("<i>" + report_data['disclaimer'] + "</i>", styles["Normal"]))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def show_report_section(diagnosis, confidence, image):
    st.markdown("### 📋 Medical Report")
    
    # Generate recommendations based on diagnosis
    recommendations = get_recommendations(diagnosis)
    
    # Create report
    report = create_medical_report(diagnosis, confidence, recommendations)
    
    # Display report preview
    with st.expander("Preview Report"):
        st.markdown(f"""
        **Date**: {report['date']}
        
        **Diagnosis**: {report['diagnosis']}
        
        **Confidence**: {report['confidence']}
        
        **Recommendations**:
        {report['recommendations']}
        
        **Disclaimer**: {report['disclaimer']}
        """)
    
    # Download options
    col1, col2 = st.columns(2)
    with col1:
        format_type = st.selectbox(
            "Select Format",
            ["PDF", "Word", "Text"]
        )
    
    with col2:
        if st.button("Download Report"):
            try:
                if format_type == "PDF":
                    # Generate PDF
                    pdf_buffer = create_pdf_report(report, image)
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                elif format_type == "Word":
                    # For Word, create a simple text version
                    report_content = download_report(report)
                    st.download_button(
                        label="Download Word Report",
                        data=report_content.encode(),
                        file_name=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.doc",
                        mime="application/msword"
                    )
                else:
                    # Text format
                    report_content = download_report(report)
                    st.download_button(
                        label="Download Text Report",
                        data=report_content.encode(),
                        file_name=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")


def get_recommendations(diagnosis):
    """Generate recommendations based on diagnosis"""
    recommendations = {
        "brain_tumor": [
            "Schedule an immediate consultation with a neurologist",
            "Get a follow-up MRI scan",
            "Monitor for any new symptoms"
        ],
        "eye_disease": [
            "Visit an ophthalmologist",
            "Protect eyes from bright light",
            "Regular eye check-ups"
        ],
        # Add more conditions and recommendations
    }
    
    # Get default recommendations if specific ones aren't found
    default_recs = [
        "Consult with a specialist",
        "Schedule regular check-ups",
        "Maintain a healthy lifestyle"
    ]
    
    return recommendations.get(diagnosis.lower(), default_recs)


if __name__ == "__main__":
    main()