import streamlit as st
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Studio Planner v2.6", layout="wide")

# CUSTOM CSS: Dark Mode original aesthetic
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sleek Day Tile Styling */
    .day-container {
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 5px;
        min-height: 85px;
        transition: transform 0.2s;
    }
    .day-container:hover { transform: translateY(-3px); cursor: pointer; }
    
    .label-text { font-size: 0.7rem; opacity: 0.7; margin-bottom: 2px; }
    .num-text { font-size: 1.3rem; font-weight: bold; margin-bottom: 2px; }
    .month-text { font-size: 0.6rem; opacity: 0.6; text-transform: uppercase; }

    /* Task Box Styling */
    .task-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- DATA HANDLING ---
DATA_FILE = "studio_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {"daily_plans": {}}
    return {"daily_plans": {}}

data = load_data()
if "daily_plans" not in data: data["daily_plans"] = {}

def save():
    with open(DATA_FILE, "w") as f: json.dump(data, f)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Tools")
    with st.expander("🪄 Template Mass-Add"):
        m_task = st.text_input("Task Description")
        m_range = st.date_input("Date Range", value=[datetime.now(), datetime.now() + timedelta(days=6)])
        if st.button("Apply Template"):
            if len(m_range) == 2:
                curr = m_range[0]
                while curr <= m_range[1]:
                    d_str = curr.strftime("%Y-%m-%d")
                    if d_str not in data["daily_plans"]: data["daily_plans"][d_str] = []
                    if not any(t['name'] == m_task for t in data["daily_plans"][d_str]):
                        data["daily_plans"][d_str].append({"name": m_task, "done": False})
                    curr += timedelta(days=1)
                save(); st.rerun()

# --- MAIN UI ---
st.title("60-Day Commitment Tracker")

def get_color_logic(date_str):
    plan = data["daily_plans"].get(date_str, [])
    if not plan: return "rgba(255,255,255,0.05)", "none", "white"
    
    total = len(plan)
    done = sum(1 for t in plan if t.get("done", False))
    percent = (done / total) * 100 if total > 0 else 0
    
    # 5-Stage Color Spectrum (Matte/Deep for visibility)
    glow = "none"
    if percent == 0: color = "#8b0000"      # Matte Red
    elif percent <= 25: color = "#a65d00"   # Matte Orange
    elif percent <= 50: color = "#9a8c00"   # Matte Yellow
    elif percent <= 75: color = "#006400"   # Matte Green
    else: 
        color = "#00f3ff"                   # Neon Blue
        glow = "0 0 15px rgba(0, 243, 255, 0.7)"
    
    # Text is black for lighter colors (Yellow/Green) for contrast
    text_c = "black" if (25 < percent < 80) else "white"
    return color, glow, text_c

# GRID DISPLAY
today = datetime.now().date()
cols = st.columns(10) 
for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    bg, glow, txt = get_color_logic(d_str)
    
    with cols[i % 10]:
        # Using a clickable button that contains the styled HTML
        if st.button(f"{day.strftime('%a')}\n{day.day}\n{day.strftime('%b')}", 
                     key=f"btn_{d_str}", 
                     use_container_width=True,
                     help=f"Plan for {d_str}"):
            st.session_state.selected_date = d_str
        
        # Injecting the color styling directly via CSS selector
        st.markdown(f"""
            <style>
                div.stButton > button[key="btn_{d_str}"] {{
                    background-color: {bg} !important;
                    box-shadow: {glow} !important;
                    color: {txt} !important;
                    white-space: pre-wrap !important;
                    border: 1px solid rgba(255,255,255,0.1) !important;
                    font-size: 0.8rem !important;
                    font-weight: bold !important;
                }}
            </style>
        """, unsafe_allow_html=True)

st.divider()

# DAY VIEW
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today.strftime("%Y-%m-%d")

sel_date = st.session_state.selected_date
st.subheader(f"Schedule for {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%A, %b %d')}")

c_list, c_add = st.columns([1.5, 1])

with c_list:
    st.markdown('<div class="task-card">', unsafe_allow_html=True)
    tasks = data["daily_plans"].get(sel_date, [])
    if not tasks:
        st.info("No tasks planned. Use the 'Quick Add' on the right.")
    else:
        for i, t in enumerate(tasks):
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            done = col1.checkbox("", value=t["done"], key=f"t_{sel_date}_{i}")
            if done != t["done"]:
                t["done"] = done
                save(); st.rerun()
            
            t_style = "color: #00F3FF; text-decoration: line-through; opacity: 0.5;" if done else "color: white;"
            col2.markdown(f"<div style='padding-top: 5px; font-size: 1.1rem; {t_style}'>{t['name']}</div>", unsafe_allow_html=True)
            if col3.button("🗑️", key=f"del_{sel_date}_{i}"):
                tasks.pop(i); save(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c_add:
    st.markdown("### ➕ Quick Add")
    new_t = st.text_input("New Task", key="new_task_field")
    if st.button("Add to Day"):
        if sel_date not in data["daily_plans"]: data["daily_plans"][sel_date] = []
        data["daily_plans"][sel_date].append({"name": new_t, "done": False})
        save(); st.rerun()
