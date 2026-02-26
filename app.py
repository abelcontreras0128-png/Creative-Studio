import streamlit as st
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Studio Planner v3.0", layout="wide")

# --- DATA HANDLING ---
DATA_FILE = "studio_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {"daily_plans": {}, "projects": []}
    return {"daily_plans": {}, "projects": []}

data = load_data()
if "daily_plans" not in data: data["daily_plans"] = {}
if "projects" not in data: data["projects"] = []

def save():
    with open(DATA_FILE, "w") as f: json.dump(data, f)

# --- CSS FOR CUSTOM BUTTONS ---
# We are styling the standard button to be a square and removing the "Schedule" ghost bar
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Force buttons to be perfect squares */
    div.stButton > button {
        aspect-ratio: 1/1 !important;
        width: 100% !important;
        padding: 0px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        transition: all 0.1s !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        white-space: pre-wrap !important;
    }

    /* Hide the annoying 'Schedule for' line space */
    .stDivider { margin-top: 10px !important; margin-bottom: 10px !important; }
    
    /* Clean up task list layout */
    .task-row { margin-bottom: -15px !important; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
today = datetime.now().date()
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today.strftime("%Y-%m-%d")

# --- MAIN UI ---
st.title("60-Day Commitment Tracker")

# 10 Column Grid using Native Columns
cols = st.columns(10)
for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    plan = data["daily_plans"].get(d_str, [])
    
    # Selection logic
    is_sel = d_str == st.session_state.selected_date
    border = "#00f3ff" if is_sel else "rgba(255,255,255,0.1)"
    
    # Color Logic
    glow = "none"
    if not plan:
        bg, txt = "rgba(255,255,255,0.05)", "#888"
    else:
        done = sum(1 for t in plan if t.get("done", False))
        pct = (done / len(plan)) * 100
        if pct == 0: bg, txt = "#8b0000", "white"
        elif pct <= 25: bg, txt = "#a65d00", "white"
        elif pct <= 50: bg, txt = "#9a8c00", "black"
        elif pct <= 75: bg, txt = "#006400", "white"
        else: 
            bg, txt = "#00f3ff", "black"
            glow = "0 0 12px rgba(0, 243, 255, 0.5)"

    # Create the clickable tile
    label = f"{day.strftime('%a')}\n{day.day}\n{day.strftime('%b')}"
    with cols[i % 10]:
        if st.button(label, key=f"tile_{d_str}"):
            st.session_state.selected_date = d_str
            st.rerun()
        
        # Inject style specifically for this button instance
        st.markdown(f"""
            <style>
                button[key="tile_{d_str}"] {{
                    background-color: {bg} !important;
                    color: {txt} !important;
                    box-shadow: {glow} !important;
                    border: 2px solid {border} !important;
                }}
            </style>
        """, unsafe_allow_html=True)

st.divider()

# --- DAY VIEW ---
sel_date = st.session_state.selected_date
st.subheader(f"Focus: {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%A, %b %d')}")

c_list, c_add = st.columns([1.5, 1])

with c_list:
    tasks = data["daily_plans"].get(sel_date, [])
    if not tasks:
        st.info("No tasks yet.")
    else:
        for i, t in enumerate(tasks):
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            if col1.checkbox("", value=t["done"], key=f"chk_{sel_date}_{i}"):
                if not t["done"]:
                    t["done"] = True
                    save(); st.rerun()
            elif t["done"]:
                t["done"] = False
                save(); st.rerun()
            
            t_style = "color: #00F3FF; text-decoration: line-through; opacity: 0.5;" if t["done"] else "color: white;"
            col2.markdown(f"<div style='padding-top: 5px; font-size: 1.1rem; {t_style}'>{t['name']}</div>", unsafe_allow_html=True)
            if col3.button("🗑️", key=f"del_{sel_date}_{i}"):
                tasks.pop(i); save(); st.rerun()

with c_add:
    st.write("### ➕ Quick Add")
    new_t = st.text_input("New Task", key="new_task_field")
    if st.button("Add to Day"):
        if sel_date not in data["daily_plans"]: data["daily_plans"][sel_date] = []
        data["daily_plans"][sel_date].append({"name": new_t, "done": False})
        save(); st.rerun()

# --- SIDEBAR PROJECT BOARD ---
with st.sidebar:
    st.title("📂 Project Board")
    p_name = st.text_input("Project Name")
    if st.button("Add"):
        data["projects"].append({"name": p_name, "status": "Parked"})
        save(); st.rerun()
    st.write("---")
    for i, p in enumerate(data["projects"]):
        st.write(f"**{p['name']}**")
        p['status'] = st.selectbox("Status", ["Active", "Parked"], index=0 if p['status']=="Active" else 1, key=f"proj_{i}")
