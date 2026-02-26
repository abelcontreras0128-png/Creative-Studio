import streamlit as st
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Studio Planner", layout="wide")

# CUSTOM CSS: Dark Mode original aesthetic with Neon Accents
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Grid Container */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 10px;
        margin-bottom: 20px;
    }
    /* Sleek Neon Tiles */
    .tile {
        border-radius: 8px;
        padding: 12px 5px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255, 255, 255, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .tile:hover {
        transform: translateY(-2px);
    }
    /* Task Styling */
    .task-container {
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
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {"projects": [], "daily_plans": {}}
    return {"projects": [], "daily_plans": {}}

data = load_data()
if "projects" not in data: data["projects"] = []
if "daily_plans" not in data: data["daily_plans"] = {}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Studio")
    with st.expander("🪄 Mass-Add Template"):
        m_task = st.text_input("Task")
        m_range = st.date_input("Range", value=[datetime.now(), datetime.now() + timedelta(days=6)])
        if st.button("Apply"):
            if len(m_range) == 2:
                curr = m_range[0]
                while curr <= m_range[1]:
                    d_str = curr.strftime("%Y-%m-%d")
                    if d_str not in data["daily_plans"]: data["daily_plans"][d_str] = []
                    if not any(t['name'] == m_task for t in data["daily_plans"][d_str]):
                        data["daily_plans"][d_str].append({"name": m_task, "done": False})
                    curr += timedelta(days=1)
                save(); st.rerun()

    with st.expander("📁 Projects"):
        p_name = st.text_input("Name")
        if st.button("Add"):
            data["projects"].append({"name": p_name, "status": "Parked"})
            save(); st.rerun()
        for i, p in enumerate(data["projects"]):
            st.write(f"**{p['name']}**")
            p['status'] = st.selectbox("State", ["Active", "Parked"], index=0 if p['status']=="Active" else 1, key=f"ps_{i}")

# --- MAIN UI ---
st.title("60-Day Daily Commitment Tracker")

def get_neon_logic(date_str):
    plan = data["daily_plans"].get(date_str, [])
    if not plan: return "rgba(255,255,255,0.05)", 0, "#888" # Grey/Empty
    
    total = len(plan)
    done = sum(1 for t in plan if t.get("done", False))
    percent = (done / total) * 100 if total > 0 else 0
    
    # 5-Stage Neon Spectrum
    if percent == 0: color = "#FF3131"      # Neon Red
    elif percent <= 25: color = "#FF5E00"   # Neon Orange
    elif percent <= 50: color = "#FFFB00"   # Neon Yellow
    elif percent <= 75: color = "#39FF14"   # Neon Green
    else: color = "#00F3FF"                  # Neon Blue
    
    return color, percent, "#FFF"

# GRID DISPLAY (10 cols to match original image)
today = datetime.now().date()
cols = st.columns(10) 
for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    color, percent, text_c = get_neon_logic(d_str)
    
    with cols[i % 10]:
        glow = f"box-shadow: 0 0 10px {color};" if percent > 0 else ""
        tile_html = f"""
        <div style="background: {color if percent > 0 else 'rgba(255,255,255,0.05)'}; 
                    {glow} border-radius: 8px; padding: 10px 5px; text-align: center; margin-bottom: 5px;">
            <div style="font-size: 0.7em; color: {text_c if percent > 0 else '#888'}; opacity: 0.8;">{day.strftime('%a')}</div>
            <div style="font-size: 1.1em; font-weight: bold; color: {text_c if percent > 0 else '#888'};">{day.day}</div>
            <div style="font-size: 0.6em; color: {text_c if percent > 0 else '#888'}; opacity: 0.8;">{day.strftime('%b')}</div>
        </div>
        """
        st.markdown(tile_html, unsafe_allow_html=True)
        if st.button("●", key=f"sel_{d_str}", use_container_width=True):
            st.session_state.selected_date = d_str

st.divider()

# DAY VIEW
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today.strftime("%Y-%m-%d")

sel_date = st.session_state.selected_date
st.subheader(f"Tasks: {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%b %d, %Y')}")

c_list, c_add = st.columns([1.5, 1])

with c_list:
    st.markdown('<div class="task-container">', unsafe_allow_html=True)
    tasks = data["daily_plans"].get(sel_date, [])
    if not tasks:
        st.info("No plans yet.")
    else:
        for i, t in enumerate(tasks):
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            done = col1.checkbox("", value=t["done"], key=f"t_{sel_date}_{i}")
            if done != t["done"]:
                t["done"] = done
                save(); st.rerun()
            
            task_style = "color: #00F3FF; text-decoration: line-through; opacity: 0.6;" if done else "color: white;"
            col2.markdown(f"<div style='padding-top: 5px; {task_style}'>{t['name']}</div>", unsafe_allow_html=True)
            if col3.button("🗑️", key=f"del_{sel_date}_{i}"):
                tasks.pop(i); save(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c_add:
    st.markdown("### ➕ Add Task")
    new_t = st.text_input("Description", key="new_task_field")
    if st.button("Add to List"):
        if sel_date not in data["daily_plans"]: data["daily_plans"][sel_date] = []
        data["daily_plans"][sel_date].append({"name": new_t, "done": False})
        save(); st.rerun()
