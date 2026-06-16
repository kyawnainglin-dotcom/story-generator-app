import streamlit as st
import google.generativeai as genai
import random

# --- Page Config ---
st.set_page_config(page_title="AI Storyboard & Script Generator", layout="wide")

# --- Custom CSS for Colorful Professional UI ---
st.markdown("""
    <style>
        /* 1. Background Image with Dark overlay */
        .stApp {
            background: linear-gradient(rgba(10, 10, 14, 0.85), rgba(10, 10, 14, 0.85)), 
                        url('https://images.unsplash.com/photo-1536440136628-849c177e76a1?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* 2. Top 30% Spacing for Content */
        .main-content { padding-top: 30vh; }
        
        /* 3. Clean Typography & Heading */
        h1 { color: #FFD700; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; }
        .sub-text { text-align: center; color: #b0b3b8; font-size: 14px; margin-bottom: 25px; letter-spacing: 0.5px; }
        
        /* 4. Text Input Field Box */
        .stTextInput > div > div > input {
            border-radius: 12px;
            background-color: rgba(255, 255, 255, 0.07);
            color: white;
            border: 1px solid #FFD700;
            padding: 12px 20px;
            font-size: 15px;
        }
        .stTextInput > div > div > input:focus {
            border: 1px solid #00ffcc;
            box-shadow: 0 0 10px rgba(0, 255, 204, 0.3);
        }
        
        /* 5. Glowing Main Generate Button */
        div.stButton > button {
            background: linear-gradient(45deg, #FFD700, #FF8C00);
            color: black;
            font-weight: bold;
            font-size: 16px;
            border-radius: 25px;
            width: 100%;
            border: none;
            padding: 10px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
        }
        div.stButton > button:hover {
            background: linear-gradient(45deg, #00ffcc, #0099ff);
            color: white;
            box-shadow: 0 4px 20px rgba(0, 255, 204, 0.4);
            transform: translateY(-2px);
        }
        
        /* 6. Colorful Sidebar Fields */
        .css-1d391kg, [data-testid="stSidebar"] {
            background-color: #0e1117 !important;
        }
        /* Sliders Color */
        .stSlider div { color: #00ffcc !important; }
        
        /* 7. Output Story Display Box (Font 14 & 12) */
        .story-container {
            background-color: rgba(17, 17, 26, 0.85);
            padding: 30px;
            border-radius: 16px;
            border: 1px solid rgba(255, 215, 0, 0.3);
            margin-top: 40px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        .story-title-style { 
            font-size: 14pt !important; 
            color: #FF8C00 !important; 
            font-weight: bold !important; 
            margin-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 10px;
        }
        .story-body-style { 
            font-size: 12pt !important; 
            color: #EAEAEA !important; 
            line-height: 1.7 !important; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Formatting for tables/markdown generated inside */
        .story-body-style h2, .story-body-style h3 { color: #FFD700; font-size: 13pt; margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)


# --- ⚙️ Sidebar Production Settings (ALL Features Restored) ---
st.sidebar.markdown("<h2 style='color: #FFD700; font-size: 20px;'>⚙️ Settings</h2>", unsafe_allow_html=True)

# 1. Duration Options
duration_min = st.sidebar.slider("Duration (Minutes)", 0, 10, 1)
duration_sec = st.sidebar.slider("Duration (Seconds)", 0, 50, 0, step=10)

# 2. Story Type Selection
story_type = st.sidebar.selectbox(
    "Story Type",
    ["Drama", "Horror", "Romance", "Fantasy", "Sci-Fi", "Comedy", "Action"]
)

# 3. Visual Art Style Options
art_style = st.sidebar.selectbox(
    "Visual Art Style",
    ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"]
)

# 4. Scene Breakdown Settings
scene_every_sec = st.sidebar.number_input("Scene Breakdown (Every X Seconds)", min_value=1, max_value=60, value=10, step=1)

# 5. Conditional Feature Toggles
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
            
            # Use high creativity setting to keep stories unique
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
            3. Layout/Language: Output everything completely in English language.
            4. Plot Concept: Based on this idea: '{story_concept}'. If the idea is empty, automatically create a fresh, stunning creative masterpiece from scratch.
            5. Visual Style: {art_style}
            6. Breakdown: Segment the total {total_seconds} seconds into intervals of {scene_every_sec} seconds each (Approximately {estimated_scenes} scenes).
            
            [Output Format Structure]
            Write a clear heading "Master Production Board Script" followed by:
            - PART 1: THE FULL STORY TEXT (Deep cinematic storytelling prose)
            - PART 2: CHARACTER PROMPTS (Midjourney prompts for key characters)
            - PART 3: SCENE BY SCENE SCRIPT BREAKDOWN:
              For each scene, provide:
              * Scene Number and Time Range
              * Narration & Dialogue
            """
            if get_image_prompt:
                command += f"\n  * Image Prompt (Midjourney formula matching style {art_style} and aspect ratio --ar {image_ratio})"
            if get_video_prompt:
                command += f"\n  * Video Prompt (Camera movement, action & dynamic environment details)"
            command += "\n  * Sound Style & Music Mood"
            
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
                    file_name=f"ai_{story_type}_script.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)
