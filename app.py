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
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {"projects": [], "daily_plans": {}}
    return {"projects": [], "daily_plans": {}}

data = load_data()
if "projects" not in data: data["projects"] = []
if "daily_plans" not in data: data["daily_plans"] = {}

def save():
    with open(DATA_FILE, "w") as f: json.dump(data, f)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Studio Tools")
    with st.expander("🪄 Template Mass-Add"):
        m_task = st.text_input("Task Description")
        m_range = st.date_input("Date Range", value=[datetime.now(), datetime.now() + timedelta(days=6)])
        if st.button("Apply to All"):
            if len(m_range) == 2:
                curr = m_range[0]
                while curr <= m_range[1]:
                    d_str = curr.strftime("%Y-%m-%d")
                    if d_str not in data["daily_plans"]: data["daily_plans"][d_str] = []
                    if not any(t['name'] == m_task for t in data["daily_plans"][d_str]):
                        data["daily_plans"][d_str].append({"name": m_task, "done": False})
                    curr += timedelta(days=1)
                save(); st.rerun()

    with st.expander("📁 Project Board"):
        p_name = st.text_input("Project Name")
        if st.button("Add Project"):
            data["projects"].append({"name": p_name, "status": "Parked"})
            save(); st.rerun()
        for i, p in enumerate(data["projects"]):
            st.write(f"**{p['name']}**")
            p['status'] = st.selectbox("Status", ["Active", "Parked"], index=0 if p['status']=="Active" else 1, key=f"ps_{i}")

# --- MAIN UI ---
st.title("60-Day Daily Commitment Tracker")

def get_tile_style(date_str):
    plan = data["daily_plans"].get(date_str, [])
    if not plan: return "rgba(255,255,255,0.05)", "none", "white"
    
    total = len(plan)
    done = sum(1 for t in plan if t.get("done", False))
    percent = (done / total) * 100 if total > 0 else 0
    
    # Color Palette: Matte for progress, Neon Glow only for 100%
    glow = "none"
    if percent == 0: color = "#8b0000"       # Deep Matte Red
    elif percent <= 25: color = "#a65d00"    # Deep Matte Orange
    elif percent <= 50: color = "#9a8c00"    # Deep Matte Yellow
    elif percent <= 75: color = "#006400"    # Deep Matte Green
    else: 
        color = "#00f3ff"                   # Neon Blue
        glow = "0 0 15px rgba(0, 243, 255, 0.6)" # Only Blue Glows
    
    return color, glow, ("black" if 25 < percent < 75 else "white")

# GRID DISPLAY
today = datetime.now().date()
cols = st.columns(10) 
for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    bg_color, glow, txt_color = get_tile_style(d_str)
    
    with cols[i % 10]:
        # Content of the button
        button_content = f"""
            <div class="date-label">{day.strftime('%a')}</div>
            <div class="date-num">{day.day}</div>
            <div class="date-month">{day.strftime('%b')}</div>
        """
        # We wrap the button's internal label in a div to control its appearance
        if st.button(" ", key=f"btn_{d_str}", help=f"View {d_str}"):
            st.session_state.selected_date = d_str
        
        # Overlay the style onto the button we just rendered
        st.markdown(f"""
            <style>
                div.stButton > button[key="btn_{d_str}"] {{
                    background-color: {bg_color} !important;
                    box-shadow: {glow} !important;
                    color: {txt_color} !important;
                }}
            </style>
            <script>
                var btn = window.parent.document.querySelectorAll('button[key="btn_{d_str}"]')[0];
                btn.innerHTML = `{button_content}`;
            </script>
        """, unsafe_allow_html=True)

st.divider()

# DAY VIEW
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today.strftime("%Y-%m-%d")

sel_date = st.session_state.selected_date
st.subheader(f"Schedule: {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%A, %b %d')}")

c_list, c_add = st.columns([1.5, 1])

with c_list:
    st.markdown('<div class="task-container">', unsafe_allow_html=True)
    tasks = data["daily_plans"].get(sel_date, [])
    if not tasks:
        st.info("No tasks for this day.")
    else:
        for i, t in enumerate(tasks):
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            done = col1.checkbox("", value=t["done"], key=f"t_{sel_date}_{i}")
            if done != t["done"]:
                t["done"] = done
                save(); st.rerun()
            
            t_style = "color: #00F3FF; text-decoration: line-through; opacity: 0.5;" if done else "color: white;"
            col2.markdown(f"<div style='padding-top:5px; {t_style}'>{t['name']}</div>", unsafe_allow_html=True)
            if col3.button("🗑️", key=f"del_{sel_date}_{i}"):
                tasks.pop(i); save(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c_add:
    st.markdown("### ➕ New Task")
    new_t = st.text_input("What's the move?", key="new_task_field")
    if st.button("Add Task"):
        if sel_date not in data["daily_plans"]: data["daily_plans"][sel_date] = []
        data["daily_plans"][sel_date].append({"name": new_t, "done": False})
        save(); st.rerun()
