import streamlit as st
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Studio Planner v2.5", layout="wide")

# CUSTOM CSS: Integrated Buttons and Refined Glow
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Make the button look like a tile */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
        padding: 10px 0px;
        height: auto;
        display: block;
        transition: all 0.2s;
        color: white !important;
    }
    div.stButton > button:hover {
        border-color: #00F3FF;
        transform: translateY(-2px);
    }
    /* Day, Num, Month text styling */
    .date-label { font-size: 0.7em; opacity: 0.8; line-height: 1; }
    .date-num { font-size: 1.2em; font-weight: bold; line-height: 1.1; }
    .date-month { font-size: 0.6em; opacity: 0.7; text-transform: uppercase; }
    
    .task-container {
        background: rgba(255, 255, 255, 0.02);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- DATA HANDLING ---
DATA_FILE = "studio_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
