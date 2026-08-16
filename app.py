import streamlit as st
from google import genai
import time
import re
import base64
import os

st.set_page_config(page_title="AI Director Master Shot-List Studio", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

image_file = "bg.jpg"
if os.path.exists(image_file):
    bin_str = get_base64_of_bin_file(image_file)
    bg_img_style = f"background-image: url('data:image/jpeg;base64,{bin_str}');"
else:
    bg_img_style = "background-image: url('https://w0.peakpx.com/wallpaper/705/104/HD-wallpaper-anime-girls-playing-games-bed-short-hair-blond.jpg');"

custom_css = f"""
<style>
    .stApp {{ {bg_img_style} background-size: cover; background-position: center top; background-attachment: fixed; }}
    .main-content {{ padding: 15px; background-color: rgba(15, 23, 42, 0.7); border-radius: 16px; margin-top: 10px; }}
    h1 {{ color: #ffffff !important; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); }}
    .sub-text {{ text-align: center; color: #ffbc00 !important; font-size: 16px; margin-bottom: 25px; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); }}
    .stTextInput > div > div > input {{ border-radius: 12px; background-color: rgba(255, 255, 255, 0.95); color: #0f172a !important; font-weight: 600; caret-color: #000000 !important; }}
    div.stButton > button {{ background: linear-gradient(45deg, #0f172a, #1e40af); color: white !important; font-weight: bold; border-radius: 25px; width: 100% !important; padding: 12px 25px !important; }}
    [data-testid="stSidebar"] {{ background-color: rgba(15, 23, 42, 0.95) !important; }}
    .stTextArea textarea {{ background-color: rgba(255, 255, 255, 0.98) !important; color: #0f172a !important; line-height: 1.7 !important; border-radius: 12px !important; padding: 15px !important; }}
    .scene-box {{ background-color: rgba(255, 255, 255, 0.95); border-left: 5px solid #1e40af; padding: 15px; border-radius: 8px; color: #0f172a; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

def get_genai_client(api_key):
    return genai.Client(api_key=api_key.strip())

# Quality မြင့်မားသော Model များကို ဦးစားပေး ခေါ်ယူသည့် Function
def generate_text_content(client, prompt_text):
    candidates = [
        'gemini-2.5-pro',
        'gemini-2.0-pro-exp-02-05',
        'gemini-1.5-pro',
        'gemini-2.0-flash',
        'gemini-1.5-flash'
    ]
    
    last_err = None
    for model_name in candidates:
        try:
            # စာလုံးရေ အရှည်ကြီး ထွက်လာစေရန် max_output_tokens: 8192 သတ်မှတ်ထားပါသည်
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config={'max_output_tokens': 8192, 'temperature': 0.75}
            )
            if response and response.text:
                return response, model_name
        except Exception as e:
            last_err = e
            continue
            
    raise Exception(f"API Error: {str(last_err)}")

if "story_stage" not in st.session_state: st.session_state.story_stage = "input"
if "approved_story" not in st.session_state: st.session_state.approved_story = ""
if "story_analysis" not in st.session_state: st.session_state.story_analysis = {}
if "extracted_scenes" not in st.session_state: st.session_state.extracted_scenes = []
if "scene_boards" not in st.session_state: st.session_state.scene_boards = {}

st.sidebar.markdown("<h2>⚙️ Production Settings</h2>", unsafe_allow_html=True)
story_language = st.sidebar.radio("Output Language", ["Myanmar", "English"])
col_min, col_sec = st.sidebar.columns(2)
duration_min = col_min.number_input("Minutes", min_value=0, max_value=40, value=10)
duration_sec = col_sec.number_input("Seconds", min_value=0, max_value=59, value=0)

story_type = st.sidebar.selectbox("Genre 1", ["Drama", "Horror", "Romance", "Fantasy", "Sci-Fi", "Comedy", "Action"])
secondary_type = st.sidebar.selectbox("Genre 2", ["None", "Action", "Drama", "Thriller", "Comedy", "Romance", "Mystery"])
art_style = st.sidebar.selectbox("Style", ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"])
image_ratio = st.sidebar.selectbox("Ratio", ["16:9", "9:16", "4:3", "1:1"])
user_api_key = st.sidebar.text_input("Gemini API Key", type="password")

st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("Director's Master Script & Shot Board")

if st.session_state.story_stage == "input":
    story_concept = st.text_input("Story Concept", placeholder="ဇာတ်လမ်းအကျဉ်း")
    total_target_seconds = (duration_min * 60) + duration_sec
    
    if st.button("Step 1: Brainstorm Master Screenplay"):
        if not user_api_key: st.error("API Key လိုအပ်ပါသည်။")
        elif total_target_seconds == 0: st.error("ကျေးဇူးပြု၍ အချိန်သတ်မှတ်ပေးပါ။")
        else:
            try:
                client = get_genai_client(user_api_key)
                
                # Loop 5 ကြိမ် စစ်ဆေးသည့် စနစ်
                max_attempts = 5
                attempt = 0
                passed_gate = False
                status_box = st.empty()
                combo_genre = story_type if secondary_type == "None" else f"{story_type} + {secondary_type}"
                
                # အချိန်အလိုက် စာလုံးရေနှင့် Scene အရေအတွက် တိကျစွာ သတ်မှတ်ပေးခြင်း
                if total_target_seconds <= 60:
                    length_instruction = "SHORT SCREENPLAY (1-2 distinct scenes, around 300 words)."
                elif total_target_seconds <= 300:
                    length_instruction = "MEDIUM SCREENPLAY (3-4 structured scenes, around 1000 words)."
                else:
                    length_instruction = "EPIC DETAILED LONG SCREENPLAY (Strictly 8 to 12 distinct scenes, around 2500+ words). Write comprehensive deep dialogues, elaborate scene descriptions, emotion, and character actions for each scene. DO NOT summarize or skip events."

                while attempt < max_attempts and not passed_gate:
                    attempt += 1
                    status_box.markdown(f"🔄 **Screenplay Generation: Loop {attempt}/{max_attempts}...**")
                    
                    try:
                        # Hollywood Master Script Command Prompting
                        story_command = f"""
                        You are an award-winning master Hollywood Screenwriter and Senior Script Doctor.
                        Write a 100% highly original, creative, deeply emotional, cinematic fictional movie screenplay based loosely on: '{story_concept}'. 
                        
                        Genre: {combo_genre}. 
                        Language: Write in {story_language}.
                        Scale Constraint: {length_instruction}
                        
                        CRITICAL SCREENWRITING DIRECTIVES:
                        1. Provide deep narrative depth, dramatic tension, character arcs, and vivid scene world-building.
                        2. Ensure every scene has explicit visual action directions and rich, natural multi-turn dialogues.
                        3. Do NOT abbreviate scenes or write summaries. Write fully expanded scenes from start to finish.
                        
                        Format:
                        📌 SCRIPT TITLE: [Title]
                        📖 FULL SCREENPLAY:
                        [Write complete scene headings like 'SCENE 1: EXT. LOCATION - DAY' followed by rich scene descriptions and full character dialogues]
                        """
                        
                        response, model_used = generate_text_content(client, story_command)
                        
                        # Safety / Blocked စစ်ဆေးခြင်း
                        if response.candidates and str(response.candidates[0].finish_reason) in ["RECITATION", "SAFETY", "8"]:
                            st.error(f"⚠️ Loop {attempt}: Gemini Safety Blocked. Retrying next loop...")
                            continue
                            
                        if response and response.text:
                            passed_gate = True
                            st.session_state.approved_story = response.text.strip()
                            st.session_state.story_analysis = {"genre": combo_genre}
                            st.session_state.story_stage = "story_ready"
                            break
                    except Exception as loop_err:
                        st.error(f"⚠️ Loop {attempt} Error: {str(loop_err)}")
                    time.sleep(1)
                
                status_box.empty()
                if passed_gate: st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

if st.session_state.story_stage in ["story_ready", "scenes_extracted"]:
    st.markdown("<h3 style='color: white;'>📖 Approved Screenplay Script</h3>", unsafe_allow_html=True)
    st.text_area("Story View", value=st.session_state.approved_story, height=350, label_visibility="collapsed")
    
    if st.button("❌ Discard Project"):
        st.session_state.story_stage = "input"
        st.session_state.approved_story = ""
        st.session_state.extracted_scenes = []
        st.session_state.scene_boards = {}
        st.rerun()

    if st.session_state.story_stage == "story_ready":
        if st.button("Separate Screenplay Into Scene Chunks"):
            try:
                client = get_genai_client(user_api_key)
                chunk_command = f"Break this script into logical individual scenes using format SCENE_BLOCK_START Scene X: Description Content: Text SCENE_BLOCK_END. Script: {st.session_state.approved_story}"
                res, _ = generate_text_content(client, chunk_command)
                raw_scenes = re.findall(r"SCENE_BLOCK_START(.*?)SCENE_BLOCK_END", res.text, flags=re.DOTALL)
                
                scenes_list = []
                for s in raw_scenes:
                    title_match = re.search(r"Scene \d+:.*", s)
                    content_match = re.search(r"Content:\s*(.*)", s, flags=re.DOTALL)
                    if title_match and content_match:
                        scenes_list.append({"title": title_match.group(0).strip(), "content": content_match.group(1).strip()})
                
                if scenes_list:
                    st.session_state.extracted_scenes = scenes_list
                    st.session_state.story_stage = "scenes_extracted"
                    st.rerun()
            except Exception as e: st.error(f"Error: {str(e)}")

    if st.session_state.story_stage == "scenes_extracted":
        if "Disney" in art_style:
            mj_style = "3D Pixar Disney Animation Style, Vibrant Clay Render, Raytracing"
            v_style = "Disney Pixar Animation Style, Smooth Motion"
        elif "Anime" in art_style:
            mj_style = "Anime Key Visual, Sharp Lineart, Vibrant Colors, --niji 6"
            v_style = "Anime Motion, Fluent 2D Animation"
        else:
            mj_style = "Cinematic Still, Film Grain, 8k Resolution, Photorealistic, --style raw --v 6.0"
            v_style = "Cinematic Movie Style, Photorealistic, Masterpiece Motion"

        for idx, scene in enumerate(st.session_state.extracted_scenes):
            is_scene_one = (idx == 0)
            
            with st.container():
                st.markdown(f"<div class='scene-box'><h4>📌 {scene['title']}</h4><p>{scene['content']}</p></div>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"🎬 Generate Shots", key=f"gen_{idx}"):
                        try:
                            client = get_genai_client(user_api_key)
                            
                            if is_scene_one:
                                char_sheet_instruction = """
                                ⚠️ CRITICAL MANDATORY LAW (ONLY FOR SCENE 1):
                                At the very top of your output, you MUST generate a dedicated '👥 CHARACTER MODEL SHEET PROFILES' block. 
                                For every key character in this screenplay, generate a detailed Midjourney Model Sheet Prompt containing:
                                - Age, Exact Height/Physique, Skin Tone, and specific Outfits.
                                - Explicit multiple turnaround expressions and angles: 'character sheet, multiple turnaround poses, front view, back view, side view, multiple facial expressions and emotional impressions'.
                                - Render Style: {art_mj_style} --ar 1:1
                                """
                                structure_format = """
                                👥 CHARACTER MODEL SHEET PROFILES:
                                * [Character Name]: [Age, Height, Skin Tone, Detailed Clothing], character sheet, multiple turnaround poses, front view, back view, side view, multiple facial expressions, Style: {art_mj_style} --ar 1:1
                                
                                --------------------------------------------------
                                """
                            else:
                                char_sheet_instruction = "Do NOT generate any Character Profiles or Model Sheets here. Start directly with the Shot List Breakdown."
                                structure_format = ""

                            shot_command = """
                            You are an expert Hollywood Cinematographer, Prompter, and Sound Director. Take this scene segment and generate a meticulous sequential Shot-by-Shot list:
                            Content: {scene_content}
                            
                            {char_sheet_clause}
                            
                            Structure Your Entire Response Exactly Like This:
                            {structure_clause}
                            
                            🎬 SHOT [Scene Number].[Shot Number] - [Duration: X Seconds]
                            
                            🎨 Image Prompt (Midjourney): [MUST start with the Camera Framing/Angle keyword, e.g., 'An extreme wide shot establishing shot of...', 'A close up shot of...']. Describe the environment and character states clearly following style: {art_mj_style} --ar {art_ratio}
                            
                            👥 DIALOGUE / NARRATION: [Character Name or N/A]: "[Script line or narration text translated to {story_lang}]"
                            
                            🎥 Video Prompt & Direction (Runway/Luma): [Combine Camera Movement like Pan/Zoom/Tilt with the characters' physical action actions], Motion Style: {art_v_style}
                            
                            🎵 Sound Style & SFX/Solfeggio: [Character voice delivery parameters] + [Audio atmosphere background music parameters for Suno/Udio]
                            
                            --------------------------------------------------
                            """.format(
                                scene_content=scene['content'],
                                char_sheet_clause=char_sheet_instruction,
                                structure_clause=structure_format,
                                story_lang=story_language,
                                art_mj_style=mj_style,
                                art_ratio=image_ratio,
                                art_v_style=v_style
                            )
                            
                            with st.spinner(f"{scene['title']} အတွက် Prompts များ ထုတ်လုပ်နေသည်..."):
                                response, _ = generate_text_content(client, shot_command)
                                if response and response.text:
                                    st.session_state.scene_boards[idx] = response.text.strip()
                                    st.rerun()
                        except Exception as e: st.error(f"API Error: {str(e)}")
                
                with col2:
                    if idx in st.session_state.scene_boards:
                        st.text_area("Shot Output", value=st.session_state.scene_boards[idx], height=300, key=f"text_{idx}")
                        st.download_button(
                            label=f"📥 Download {scene['title']} Board", 
                            data=st.session_state.scene_boards[idx], 
                            file_name=f"scene_{idx}_master_board.txt", 
                            key=f"dl_{idx}"
                        )

st.markdown("</div>", unsafe_allow_html=True)
