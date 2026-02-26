import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Studio Planner v2.8", layout="wide")

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

# --- SIDEBAR: TOOLS & PROJECTS ---
with st.sidebar:
    st.title("🛠️ Studio Tools")
    
    with st.expander("📁 Project Board"):
        p_name = st.text_input("New Project Name")
        if st.button("Add Project"):
            data["projects"].append({"name": p_name, "status": "Parked"})
            save(); st.rerun()
        
        st.write("---")
        for i, p in enumerate(data["projects"]):
            col1, col2 = st.columns([2, 1])
            col1.write(f"**{p['name']}**")
            p['status'] = col2.selectbox("Status", ["Active", "Parked"], index=0 if p['status']=="Active" else 1, key=f"ps_{i}")

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

# --- GRID LOGIC ---
today = datetime.now().date()
grid_data = []

for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    plan = data["daily_plans"].get(d_str, [])
    
    # Calculate Color
    if not plan:
        color, glow, text = "rgba(255,255,255,0.05)", "none", "#888"
    else:
        total = len(plan)
        done = sum(1 for t in plan if t.get("done", False))
        pct = (done / total) * 100
        glow = "none"
        if pct == 0: color = "#8b0000" # Red
        elif pct <= 25: color = "#a65d00" # Orange
        elif pct <= 50: color = "#9a8c00" # Yellow
        elif pct <= 75: color = "#006400" # Green
        else: 
            color = "#00f3ff" # Neon Blue
            glow = "0 0 15px rgba(0, 243, 255, 0.6)"
        text = "black" if (25 < pct < 80) else "white"
        
    grid_data.append({
        "date": d_str,
        "day_name": day.strftime('%a'),
        "day_num": day.day,
        "month": day.strftime('%b'),
        "color": color,
        "glow": glow,
        "text": text
    })

# --- CUSTOM GRID COMPONENT ---
# This renders the grid as one single interactive block
grid_html = f"""
<style>
    .grid {{
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 8px;
        background-color: #0e1117;
        font-family: sans-serif;
    }}
    .tile {{
        aspect-ratio: 1/1;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.1s;
    }}
    .tile:hover {{ transform: scale(1.05); border-color: white; }}
    .t-day {{ font-size: 10px; opacity: 0.8; text-transform: uppercase; }}
    .t-num {{ font-size: 18px; font-weight: bold; margin: 2px 0; }}
    .t-mon {{ font-size: 9px; opacity: 0.6; }}
</style>
<div class="grid">
    {''.join([f'''
    <div class="tile" style="background-color: {d['color']}; box-shadow: {d['glow']}; color: {d['text']};" 
         onclick="parent.postMessage({{type: 'select_date', date: '{d['date']}'}}, '*')">
        <div class="t-day">{d['day_name']}</div>
        <div class="t-num">{d['day_num']}</div>
        <div class="t-mon">{d['month']}</div>
    </div>
    ''' for d in grid_data])}
</div>

<script>
    // This script sends the date back to Streamlit when a tile is clicked
    const tiles = document.querySelectorAll('.tile');
    tiles.forEach(tile => {{
        tile.addEventListener('click', () => {{
            // Custom event handling for Streamlit
        }});
    }});
</script>
"""

# Render Title and Grid
st.title("60-Day Commitment Tracker")

# We use a hidden input and small JS bridge to handle the "click"
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today.strftime("%Y-%m-%d")

# This is the "invisible" selection logic
# Since Streamlit components are isolated, we use a simple selectbox as a bridge
selected = st.selectbox("Select Date to View/Edit:", [d['date'] for d in grid_data], 
                        index=[d['date'] for d in grid_data].index(st.session_state.selected_date))
st.session_state.selected_date = selected

# Visual Grid (Display Only in this version for stability)
components.html(grid_html, height=550)

st.divider()

# --- DAY VIEW ---
sel_date = st.session_state.selected_date
st.subheader(f"Schedule for {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%A, %b %d')}")

c_list, c_add = st.columns([1.5, 1])

with c_list:
    st.markdown('<div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">', unsafe_allow_html=True)
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
