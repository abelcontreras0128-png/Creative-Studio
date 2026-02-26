import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Studio Planner v2.9", layout="wide")

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

# --- SESSION STATE INITIALIZATION ---
today = datetime.now().date()
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today.strftime("%Y-%m-%d")

# --- SIDEBAR: PROJECTS ---
with st.sidebar:
    st.title("📂 Project Board")
    p_name = st.text_input("New Project Name")
    if st.button("Add Project"):
        data["projects"].append({"name": p_name, "status": "Parked"})
        save(); st.rerun()
    st.write("---")
    for i, p in enumerate(data["projects"]):
        with st.expander(f"Edit: {p['name']}"):
            p['name'] = st.text_input("Rename", value=p['name'], key=f"ren_{i}")
            p['status'] = st.selectbox("Status", ["Active", "Parked"], index=0 if p['status']=="Active" else 1, key=f"stat_{i}")

# --- GRID CALCULATION ---
grid_data = []
for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    plan = data["daily_plans"].get(d_str, [])
    
    # Selection Highlight
    is_selected = d_str == st.session_state.selected_date
    border = "2px solid #00f3ff" if is_selected else "1px solid rgba(255,255,255,0.1)"
    
    # Color Logic
    if not plan:
        color, glow, text = "rgba(255,255,255,0.05)", "none", "#888"
    else:
        done = sum(1 for t in plan if t.get("done", False))
        pct = (done / len(plan)) * 100
        glow = "none"
        if pct == 0: color = "#8b0000" # Red
        elif pct <= 25: color = "#a65d00" # Orange
        elif pct <= 50: color = "#9a8c00" # Yellow
        elif pct <= 75: color = "#006400" # Green
        else: 
            color = "#00f3ff" # Neon Blue
            glow = "0 0 15px rgba(0, 243, 255, 0.6)"
        
        # FIXING LEGIBILITY: Black text for bright Neon Blue or Yellow
        text = "black" if (pct > 75 or 25 < pct < 55) else "white"
        
    grid_data.append({
        "date": d_str, "day_name": day.strftime('%a'), "day_num": day.day,
        "month": day.strftime('%b'), "color": color, "glow": glow, "text": text, "border": border
    })

# --- COMPONENT HTML (The Clickable Grid) ---
# We use query params as a "hack" to send data from HTML back to Python instantly
grid_html = f"""
<style>
    .grid {{ display: grid; grid-template-columns: repeat(10, 1fr); gap: 8px; font-family: sans-serif; }}
    .tile {{
        aspect-ratio: 1/1; border-radius: 8px; display: flex; flex-direction: column;
        justify-content: center; align-items: center; cursor: pointer; transition: 0.1s;
    }}
    .tile:hover {{ transform: scale(1.03); }}
    .t-day {{ font-size: 10px; opacity: 0.8; text-transform: uppercase; }}
    .t-num {{ font-size: 18px; font-weight: bold; margin: 2px 0; }}
    .t-mon {{ font-size: 9px; opacity: 0.6; }}
</style>
<div class="grid">
    {''.join([f'''
    <div class="tile" style="background-color: {d['color']}; box-shadow: {d['glow']}; color: {d['text']}; border: {d['border']};" 
         onclick="window.parent.postMessage({{type: 'streamlit:set_query_params', params: {{selected: '{d['date']}'}}}}, '*')">
        <div class="t-day">{d['day_name']}</div>
        <div class="t-num">{d['day_num']}</div>
        <div class="t-mon">{d['month']}</div>
    </div>
    ''' for d in grid_data])}
</div>
"""

# Check if a click happened via query params
q_params = st.query_params
if "selected" in q_params and q_params["selected"] != st.session_state.selected_date:
    st.session_state.selected_date = q_params["selected"]
    st.rerun()

st.title("60-Day Commitment Tracker")
components.html(grid_html, height=520)

# --- DAY VIEW ---
st.divider()
sel_date = st.session_state.selected_date
st.subheader(f"Schedule: {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%A, %b %d')}")

c_list, c_add = st.columns([1.5, 1])

with c_list:
    tasks = data["daily_plans"].get(sel_date, [])
    if not tasks:
        st.info("No tasks yet. Plan this day on the right.")
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

with c_add:
    st.write("### ➕ Quick Add")
    new_t = st.text_input("Task Name", key="new_task_field", placeholder="e.g. Finish Chapter 1")
    if st.button("Add to Day"):
        if sel_date not in data["daily_plans"]: data["daily_plans"][sel_date] = []
        data["daily_plans"][sel_date].append({"name": new_t, "done": False})
        save(); st.rerun()
