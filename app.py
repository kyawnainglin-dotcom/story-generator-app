import streamlit as st
import google.generativeai as genai
import time

# --- Page Config ---
st.set_page_config(page_title="AI Storyboard Generator", layout="wide")

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
        /* Background Image */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                        url('https://images.unsplash.com/photo-1536440136628-849c177e76a1?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
        }
        
        /* Top Spacing */
        .main { padding-top: 30vh; }
        
        /* Header Styling */
        h1 { color: #FFD700; text-align: center; font-family: 'Helvetica', sans-serif; }
        
        /* Input Box Styling */
        .stTextInput > div > div > input {
            border-radius: 20px;
            background-color: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid #FFD700;
        }
        
        /* Button Styling */
        div.stButton > button {
            background-color: #FFD700;
            color: black;
            font-weight: bold;
            border-radius: 20px;
            width: 100%;
            border: none;
            transition: 0.3s;
        }
        div.stButton > button:hover { background-color: #ffffff; }
        
        /* Story Box Styling */
        .story-box {
            background-color: rgba(0,0,0,0.6);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #444;
        }
        .story-title { font-size: 14pt; color: #FFD700; font-weight: bold; }
        .story-body { font-size: 12pt; color: #ffffff; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Cleanup ---
st.sidebar.markdown("### Settings")
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- Main Page Content ---
st.markdown("<div class='main'>", unsafe_allow_html=True)
st.title("Storyboard Script Generator")
st.markdown("<p style='text-align: center; color: #ccc;'>Create the best story here</p>", unsafe_allow_html=True)

story_concept = st.text_input("", placeholder="Write your story concept here...")

if st.button("Generate Script"):
    if not user_api_key:
        st.error("Please enter your API Key in the sidebar.")
    else:
        try:
            genai.configure(api_key=user_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner('Crafting your masterpiece...'):
                prompt = f"Write a creative and professional storyboard script based on this concept: {story_concept}. Use a cinematic storytelling style. Title: 14pt equivalent, Body: 12pt equivalent tone."
                response = model.generate_content(prompt)
                
                # Display Result in Custom Box
                st.markdown("<div class='story-box'>", unsafe_allow_html=True)
                st.markdown(f"<div class='story-title'>Story Output</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='story-body'>{response.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
st.markdown("</div>", unsafe_allow_html=True)
