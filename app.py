import streamlit as st
import google.generativeai as genai
import random

# --- Page Config ---
st.set_page_config(page_title="AI Storyboard & Script Generator", layout="wide")

# --- Custom CSS for Light Professional UI ---
st.markdown("""
    <style>
        /* 1. Clean & Bright Light Background */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* 2. Top 30% Spacing for Content */
        .main-content { padding-top: 30vh; }
        
        /* 3. Clean Typography & Heading (Light Mode) */
        h1 { color: #1e3a8a; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; }
        .sub-text { text-align: center; color: #4b5563; font-size: 15px; margin-bottom: 25px; letter-spacing: 0.5px; font-weight: 500; }
        
        /* 4. Text Input Field Box (Light Mode Style) */
        .stTextInput > div > div > input {
            border-radius: 12px;
            background-color: rgba(255, 255, 255, 0.9);
            color: #1f2937;
            border: 2px solid #1e3a8a;
            padding: 14px 20px;
            font-size: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stTextInput > div > div > input:focus {
            border: 2px solid #3b82f6;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
        }
        
        /* 5. Perfect Full-Width Generate Button with No Text Clipping */
        div.stButton > button {
            background: linear-gradient(45deg, #1e3a8a, #3b82f6);
            color: white !important;
            font-weight: bold;
            font-size: 16px;
            border-radius: 25px;
            width: 100% !important; /* Forces it to occupy full layout width */
            min-width: 200px;       /* Ensures it never shrinks too small */
            border: none;
            padding: 12px 30px !important; /* Extra padding inside to give text space */
            display: block;
            margin: 0 auto;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(30, 58, 138, 0.2);
        }
        div.stButton > button:hover {
            background: linear-gradient(45deg, #2563eb, #60a5fa);
            color: white !important;
            box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
            transform: translateY(-2px);
        }
        
        /* 6. Clean Sidebar Panel for Light Mode */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e5e7eb;
        }
        
        /* 7. Output Story Display Box (Light Mode - Font 14 & 12) */
        .story-container {
            background-color: #ffffff;
            padding: 35px;
            border-radius: 16px;
            border: 1px solid #e5e7eb;
            margin-top: 40px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        }
        .story-title-style { 
            font-size: 14pt !important; 
            color: #1e3a8a !important; 
            font-weight: bold !important; 
            margin-bottom: 15px;
            border-bottom: 2px solid #f3f4f6;
            padding-bottom: 10px;
        }
        .story-body-style { 
            font-size: 12pt !important; 
            color: #374151 !important; 
            line-height: 1.8 !important; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Inner markdown text formatting */
        .story-body-style h2, .story-body-style h3 { color: #2563eb; font-size: 13pt; margin-top: 25px; }
    </style>
""", unsafe_allow_html=True)


# --- ⚙️ Sidebar Production Settings ---
st.sidebar.markdown("<h2 style='color: #1e3a8a; font-size: 20px; font-weight: bold;'>⚙️ Settings</h2>", unsafe_allow_html=True)

# 1. Output Story Language
story_language = st.sidebar.radio(
    "Story Language (Output)",
    ["Myanmar", "English"]
)

st.sidebar.markdown("---")

# 2. Duration Options
duration_min = st.sidebar.slider("Duration (Minutes)", 0, 10, 1)
duration_sec = st.sidebar.slider("Duration (Seconds)", 0, 50, 0, step=10)

# 3. Story Type Selection
story_type = st.sidebar.selectbox(
    "Story Type",
    ["Drama", "Horror", "Romance", "Fantasy", "Sci-Fi", "Comedy", "Action"]
)

# 4. Visual Art Style Options
art_style = st.sidebar.selectbox(
    "Visual Art Style",
    ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"]
)

# 5. Scene Breakdown Settings
scene_every_sec = st.sidebar.number_input("Scene Breakdown (Every X Seconds)", min_value=5, max_value=60, value=10, step=5)

# 6. Conditional Feature Toggles
get_image_prompt = st.sidebar.checkbox("Generate Image Prompts", value=True)
get_video_prompt = st.sidebar.checkbox("Generate Video Prompts", value=False)
image_ratio = st.sidebar.selectbox("Midjourney Ratio (--ar)", ["16:9", "9:16", "4:3", "1:1"])

st.sidebar.markdown("---")
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
st.sidebar.markdown("[Get Free API Key](https://aistudio.google.com)")


# --- 🎬 Main UI Layout ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("Storyboard Script Generator")
st.markdown("<div class='sub-text'>Create the best story here</div>", unsafe_allow_html=True)

# Input Field Box
story_concept = st.text_input("", placeholder="ဇတ်လမ်းရေးရန်")

# Main Generate Button
if st.button("Generate"):
    if not user_api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    else:
        try:
            genai.configure(api_key=user_api_key)
            
            # High creativity configurations
            generation_config = {
                "temperature": 0.95, 
                "top_p": 0.95,
                "top_k": 40,
            }
            
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                generation_config=generation_config
            )
            
            total_seconds = (duration_min * 60) + duration_sec
            estimated_scenes = max(1, total_seconds // scene_every_sec)
            random_seed = random.randint(1, 100000)
            
            # --- Constructing AI Master Prompt ---
            command = f"""
            You are a world-class professional Scriptwriter and Director (AI Director).
            Create a unique, captivating, and highly distinct storyboard script. Do NOT repeat previous cliché plots. (Seed Key: {random_seed})
            
            [Specifications]
            1. Target Duration: {duration_min} minutes and {duration_sec} seconds.
            2. Genre: {story_type}
            3. Story Language: Output the main story, dialogues, and script text in {story_language} language. (Note: Tech prompts like Midjourney prompts must remain in English).
            4. Plot Concept: Based on this idea: '{story_concept}'. If the idea is empty, automatically create a fresh, stunning creative masterpiece from scratch.
            5. Visual Style: {art_style}
            6. Breakdown: Segment the total {total_seconds} seconds into intervals of {scene_every_sec} seconds each (Approximately {estimated_scenes} scenes).
            
            [Output Format Structure]
            Write a clear heading "Master Production Board Script" followed by:
            - PART 1: THE FULL STORY TEXT (Deep cinematic storytelling prose written in {story_language})
            - PART 2: CHARACTER PROMPTS (Midjourney prompts for key characters in English)
            - PART 3: SCENE BY SCENE SCRIPT BREAKDOWN:
              For each scene, provide:
              * Scene Number and Time Range
              * Narration & Dialogue (Written in {story_language})
            """
            if get_image_prompt:
                command += f"\n  * Image Prompt (Midjourney formula in English matching style {art_style} and aspect ratio --ar {image_ratio})"
            if get_video_prompt:
                command += f"\n  * Video Prompt (Camera movement, action & dynamic environment details in English)"
            command += f"\n  * Sound Style & Music Mood (In English)"
            
            # Elegant Custom Loading Spinner
            with st.spinner("⚡ Crafting and producing your cinematic masterpiece..."):
                response = model.generate_content(command)
                result_text = response.text
                
                # Render the Output inside the stylized 14pt/12pt Container
                st.markdown("<div class='story-container'>", unsafe_allow_html=True)
                st.markdown("<div class='story-title-style'>🎬 Master Production Board & Story Output</div>", unsafe_allow_html=True)
                
                # Convert newlines to HTML breaks for proper layout render
                formatted_story = result_text.replace("\n", "<br>")
                st.markdown(f"<div class='story-body-style'>{formatted_story}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Clean Download Feature
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download Master Script File (.txt)",
                    data=result_text,
                    file_name=f"ai_{story_type}_{story_language.lower()}_script.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)
