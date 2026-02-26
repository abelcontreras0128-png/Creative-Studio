import streamlit as st
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Studio Planner v2.7", layout="wide")

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

# --- CUSTOM CSS FOR UNIFORMITY ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Grid Container: Fixed 10 columns for desktop, wraps for mobile */
    .planner-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
        gap: 8px;
        margin-bottom: 30px;
    }

    /* Uniform Square Tile */
    .day-tile {
        aspect-ratio: 1 / 1;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.1);
        text-decoration: none;
        transition: transform 0.1s, box-shadow 0.2s;
        cursor: pointer;
    }
    
    .day-tile:hover { transform: scale(1.05); }

    .t-day { font-size: 0.65rem; opacity: 0.8; text-transform: uppercase; }
    .t-num { font-size: 1.2rem; font-weight: bold; margin: 2px 0; }
    .t-mon { font-size: 0.6rem; opacity: 0.6; }

    .task-area {
        background: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

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

def get_day_style(date_str):
    plan = data["daily_plans"].get(date_str, [])
    if not plan: return "rgba(255,255,255,0.05)", "none", "white"
    
    total = len(plan)
    done = sum(1 for t in plan if t.get("done", False))
    percent = (done / total) * 100 if total > 0 else 0
    
    glow = "none"
    if percent == 0: color = "#8b0000"
    elif percent <= 25: color = "#a65d00"
    elif percent <= 50: color = "#9a8c00"
    elif percent <= 75: color = "#006400"
    else: 
        color = "#00f3ff"
        glow = "0 0 15px rgba(0, 243, 255, 0.6)"
    
    text_c = "black" if (25 < percent < 80) else "white"
    return color, glow, text_c

# RENDER GRID
today = datetime.now().date()
cols = st.columns(10) # Using columns for click-capture
for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    bg, glow, txt = get_day_style(d_str)
    
    with cols[i % 10]:
        # The Tile UI
        st.markdown(f"""
            <div style="
                background-color: {bg};
                box-shadow: {glow};
                color: {txt};
                aspect-ratio: 1/1;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                border: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 10px;
                pointer-events: none;
            ">
                <div class="t-day">{day.strftime('%a')}</div>
                <div class="t-num">{day.day}</div>
                <div class="t-mon">{day.strftime('%b')}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Transparent button on top for clicking
        if st.button("view", key=f"sel_{d_str}", use_container_width=True):
            st.session_state.selected_date = d_str
        
        # Style the tiny 'view' button to be nearly invisible but functional
        st.markdown(f"""
            <style>
                div.stButton > button[key="sel_{d_str}"] {{
                    margin-top: -45px;
                    height: 40px;
                    opacity: 0;
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
    st.markdown('<div class="task-area">', unsafe_allow_html=True)
    tasks = data["daily_plans"].get(sel_date, [])
    if not tasks:
        st.info("No tasks yet.")
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
