import streamlit as st
import google.generativeai as genai
import random

# --- Page Config ---
st.set_page_config(page_title="AI Storyboard & Script Generator", layout="wide")

# --- Custom CSS for Premium Visuals, Clean Contrast & Full Width Buttons ---
st.markdown("""
    <style>
        /* 1. Raw Background Photo (NO MASK) - High Clarity */
        .stApp {
            background-image: url('https://www.un.org/sites/un2.un.org/files/2020/01/the-floating-gardens-of-lake-inle.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* 2. Content Layout Top Spacing */
        .main-content { padding-top: 30vh; }
        
        /* 3. Deep Dark Contrast Typography for Crisp Text Visibility over Light Background */
        h1 { color: #0f172a !important; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; }
        .sub-text { text-align: center; color: #1e293b; font-size: 16px; margin-bottom: 25px; letter-spacing: 0.5px; font-weight: 700; }
        
        /* 4. Translucent Input Box for Modern Look */
        .stTextInput > div > div > input {
            border-radius: 12px;
            background-color: rgba(255, 255, 255, 0.9);
            color: #0f172a;
            border: 2px solid #334155;
            padding: 14px 20px;
            font-size: 16px;
            font-weight: 500;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        .stTextInput > div > div > input:focus {
            border: 2px solid #1e40af;
            box-shadow: 0 0 12px rgba(30, 64, 175, 0.25);
        }
        
        /* 5. Sleek Full-Width Action Button */
        div.stButton > button {
            background: linear-gradient(45deg, #0f172a, #1e40af);
            color: white !important;
            font-weight: bold;
            font-size: 16px;
            border-radius: 25px;
            width: 100% !important;
            border: none;
            padding: 14px 30px !important;
            display: block;
            margin: 0 auto;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(15, 23, 42, 0.2);
        }
        div.stButton > button:hover {
            background: linear-gradient(45deg, #1e40af, #2563eb);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35);
            transform: translateY(-2px);
        }
        
        /* 6. Luxury Deep Navy Blue Sidebar (Navigation Bar) */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important; 
            border-right: 1px solid #1e293b;
        }
        
        /* Sidebar Elements Color Tuning for Maximum Contrast */
        [data-testid="stSidebar"] .stMarkdown h2 { color: #ffbc00 !important; font-weight: bold; letter-spacing: 0.5px; }
        [data-testid="stSidebar"] label { color: #f8fafc !important; font-weight: 600 !important; font-size: 14px !important; }
        
        /* Fixing White-on-White Checkbox Text Bug */
        [data-testid="stSidebar"] .stCheckbox p { color: #f8fafc !important; font-weight: 600 !important; }
        
        /* Radio text color adjust */
        [data-testid="stSidebar"] .stRadio div { color: #f8fafc !important; }
        
        /* 7. Output Result Container Panel */
        .story-container {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 35px;
            border-radius: 16px;
            border: 1px solid #cbd5e1;
            margin-top: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
        }
        .story-title-style { 
            font-size: 14pt !important; 
            color: #1e40af !important; 
            font-weight: bold !important; 
            margin-bottom: 15px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        .story-body-style { 
            font-size: 12pt !important; 
            color: #0f172a !important; 
            line-height: 1.8 !important; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .story-body-style h2, .story-body-style h3 { color: #1e40af; font-size: 13pt; margin-top: 25px; }
    </style>
""", unsafe_allow_html=True)


# --- ⚙️ Sidebar Navigation Panel (Deep Navy Blue) ---
st.sidebar.markdown("<h2 style='font-size: 22px;'>⚙️ Settings</h2>", unsafe_allow_html=True)

# 1. Output Story Language Selection
story_language = st.sidebar.radio(
    "Story Language (Output)",
    ["Myanmar", "English"]
)

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

# 2. Duration Settings
duration_min = st.sidebar.slider("Duration (Minutes)", 0, 10, 1)
duration_sec = st.sidebar.slider("Duration (Seconds)", 0, 50, 0, step=10)

# 3. Content Type Filter
story_type = st.sidebar.selectbox(
    "Story Type",
    ["Drama", "Horror", "Romance", "Fantasy", "Sci-Fi", "Comedy", "Action"]
)

# 4. Cinematic Art Profiles
art_style = st.sidebar.selectbox(
    "Visual Art Style",
    ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"]
)

# 5. Production Pace Configuration
scene_every_sec = st.sidebar.number_input("Scene Breakdown (Every X Seconds)", min_value=5, max_value=60, value=10, step=5)

# 6. Technical Framework Output Selectors (Color Fixed)
get_image_prompt = st.sidebar.checkbox("Generate Image Prompts", value=True)
get_video_prompt = st.sidebar.checkbox("Generate Video Prompts", value=False)
image_ratio = st.sidebar.selectbox("Midjourney Ratio (--ar)", ["16:9", "9:16", "4:3", "1:1"])

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
st.sidebar.markdown("[Get Free API Key](https://aistudio.google.com)")


# --- 🎬 Main Frame Screen Display ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("Storyboard Script Generator")
st.markdown("<div class='sub-text'>Create the best story here</div>", unsafe_allow_html=True)

# Prompt Text Area Box
story_concept = st.text_input("", placeholder="ဇတ်လမ်းရေးရန်")

# Render Engine Trigger Controller
if st.button("Generate"):
    if not user_api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    else:
        try:
            genai.configure(api_key=user_api_key)
            
            generation_config = {
                "temperature": 0.95, 
                "top_p": 0.95,
                "top_k": 40,
            }
            
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                generation_config=generation_config
            )
            
            total_seconds = (duration_min * 60) + duration_sec
            estimated_scenes = max(1, total_seconds // scene_every_sec)
            random_seed = random.randint(1, 100000)
            
            # Master Script Prompter System
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
            
            with st.spinner("⚡ Crafting and producing your cinematic masterpiece..."):
                response = model.generate_content(command)
                result_text = response.text
                
                # Render Block Text Layout View
                st.markdown("<div class='story-container'>", unsafe_allow_html=True)
                st.markdown("<div class='story-title-style'>🎬 Master Production Board & Story Output</div>", unsafe_allow_html=True)
                
                formatted_story = result_text.replace("\n", "<br>")
                st.markdown(f"<div class='story-body-style'>{formatted_story}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Document Data Downloader Service
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
