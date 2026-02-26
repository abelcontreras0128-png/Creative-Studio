import streamlit as st
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Creative Studio v2.3", layout="wide")

# Custom CSS for Sleek UI and Neon Blue Accents
st.markdown("""
<style>
    .stButton>button {
        border-radius: 12px;
        height: 70px;
        border: 1px solid #f0f2f6;
        background-color: #ffffff;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #00f3ff;
        box-shadow: 0 4px 15px rgba(0, 243, 255, 0.3);
    }
    .day-tile {
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s;
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

# --- SIDEBAR TOOLS ---
with st.sidebar:
    st.title("📂 Studio Controls")
    with st.expander("🪄 Template Mass-Add"):
        m_task = st.text_input("Task Name")
        m_range = st.date_input("Date Range", value=[datetime.now(), datetime.now() + timedelta(days=4)])
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

    with st.expander("📝 Project Board"):
        p_name = st.text_input("Project Name")
        p_form = st.text_input("Format Type")
        if st.button("Add Project"):
            data["projects"].append({"name": p_name, "format": p_form, "status": "Parked"})
            save(); st.rerun()
        for i, p in enumerate(data["projects"]):
            st.write(f"**{p['name']}** ({p['format']})")
            p['status'] = st.selectbox("Status", ["Active", "Parked"], index=0 if p['status']=="Active" else 1, key=f"ps_{i}")

# --- MAIN UI ---
st.title("✨ 60-Day Digital Planner")

def get_percent_color(date_str):
    plan = data["daily_plans"].get(date_str, [])
    if not plan: return "#f9f9f9", 0, "#333" # Empty state
    
    total = len(plan)
    done = sum(1 for t in plan if t.get("done", False))
    percent = (done / total) * 100 if total > 0 else 0
    
    # 5-Stage Neon Palette
    if percent == 0: color = "#ff4b4b"       # Red
    elif percent <= 33: color = "#ffa500"    # Orange
    elif percent <= 66: color = "#ffeb3b"    # Yellow
    elif percent < 100: color = "#00bcd4"    # Soft Cyan
    else: color = "#00f3ff"                  # Vibrant Neon Blue
    
    text_color = "#000" if percent > 0 else "#666"
    return color, percent, text_color

# GRID DISPLAY
today = datetime.now().date()
cols = st.columns(6) 
for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    color, percent, text_c = get_percent_color(d_str)
    
    with cols[i % 6]:
        tile_style = f"""
        background-color: {color}; 
        border: 2px solid {'#00f3ff' if percent == 100 else '#eee'};
        box-shadow: {'0 0 15px rgba(0, 243, 255, 0.4)' if percent == 100 else 'none'};
        """
        
        st.markdown(f"""
        <div style="{tile_style} padding: 15px; border-radius: 12px; text-align: center;">
            <div style="font-size: 0.8em; color: {text_c};">{day.strftime('%a')}</div>
            <div style="font-size: 1.2em; font-weight: bold; color: {text_c};">{day.day}</div>
            <div style="font-size: 0.7em; color: {text_c};">{day.strftime('%b')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Select {day.day}", key=f"btn_{d_str}", use_container_width=True):
            st.session_state.selected_date = d_str

st.divider()

# DAY VIEW
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today.strftime("%Y-%m-%d")

sel_date = st.session_state.selected_date
st.subheader(f"📅 Plan for {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%A, %B %d')}")

c_list, c_add = st.columns([2, 1])

with c_list:
    tasks = data["daily_plans"].get(sel_date, [])
    if not tasks:
        st.info("Click 'Add Task' on the right to start this day.")
    else:
        for i, t in enumerate(tasks):
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            done = col1.checkbox("", value=t["done"], key=f"t_{sel_date}_{i}")
            if done != t["done"]:
                t["done"] = done
                save(); st.rerun()
            
            # Neon blue strike-through for completed tasks
            task_text = f"<span style='color: #00f3ff; text-decoration: line-through;'>{t['name']}</span>" if done else t['name']
            col2.markdown(f"<div style='padding-top: 5px;'>{task_text}</div>", unsafe_allow_html=True)
            
            if col3.button("🗑️", key=f"del_{sel_date}_{i}"):
                tasks.pop(i); save(); st.rerun()

with c_add:
    st.write("### Quick Add")
    new_t = st.text_input("New Task Description", key="input_new_task")
    if st.button("Add to Today"):
        if sel_date not in data["daily_plans"]: data["daily_plans"][sel_date] = []
        data["daily_plans"][sel_date].append({"name": new_t, "done": False})
        save(); st.rerun()
