import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Creative Studio v2.1", layout="wide")

# --- DATA HANDLING ---
DATA_FILE = "studio_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {"projects": [], "daily_plans": {}}
    return {"projects": [], "daily_plans": {}}

data = load_data()

# Ensure keys exist
if "projects" not in data: data["projects"] = []
if "daily_plans" not in data: data["daily_plans"] = {}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- SIDEBAR: TOOLS ---
st.sidebar.title("🛠️ Tools & Projects")

# 1. MASS ADD TASKS (NEW FEATURE)
with st.sidebar.expander("🪄 Mass-Add Task Templates"):
    st.write("Apply a task to multiple days at once.")
    mass_task_name = st.text_input("Task Description", key="mass_t_input")
    date_range = st.date_input("Select Date Range", value=[datetime.now(), datetime.now() + timedelta(days=4)])
    
    if st.button("Apply to All Dates"):
        if len(date_range) == 2:
            start_date, end_date = date_range
            curr = start_date
            while curr <= end_date:
                d_str = curr.strftime("%Y-%m-%d")
                if d_str not in data["daily_plans"]:
                    data["daily_plans"][d_str] = []
                # Avoid duplicates
                if not any(t['name'] == mass_task_name for t in data["daily_plans"][d_str]):
                    data["daily_plans"][d_str].append({"name": mass_task_name, "done": False})
                curr += timedelta(days=1)
            save()
            st.success(f"Added to { (end_date - start_date).days + 1 } days!")
            st.rerun()

# 2. PROJECT BOARD
with st.sidebar.expander("📁 Project Board"):
    new_name = st.text_input("Project Name")
    new_format = st.text_input("Custom Format")
    if st.button("Add Project"):
        data["projects"].append({"name": new_name, "format": new_format, "status": "Parked"})
        save()
        st.rerun()
    
    st.write("---")
    for i, p in enumerate(data["projects"]):
        with st.expander(f"Edit: {p['name']}"):
            p['name'] = st.text_input("Rename", value=p['name'], key=f"ren_{i}")
            p['status'] = st.selectbox("Status", ["Active", "Parked"], index=0 if p['status']=="Active" else 1, key=f"stat_{i}")
            if st.button("Delete", key=f"del_{i}"):
                data["projects"].pop(i)
                save()
                st.rerun()

# --- MAIN UI ---
st.title("📅 60-Day Forward Planner")

# GRID LOGIC
def get_color(date_str):
    plan = data["daily_plans"].get(date_str, [])
    if not plan: return "gray"
    
    total = len(plan)
    done = sum(1 for t in plan if t.get("done", False))
    today_obj = datetime.now().date()
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    if total > 0 and done == total: return "green"
    if done > 0: return "orange"
    if date_obj < today_obj and done == 0: return "red"
    return "#444" # Planned/Future

# GRID DISPLAY
today = datetime.now().date()
cols = st.columns(10)
for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    bg = get_color(d_str)
    
    with cols[i % 10]:
        # Visual square button
        if st.button(f"{day.month}/{day.day}", key=f"btn_{d_str}", use_container_width=True, help=f"Status for {d_str}"):
            st.session_state.selected_date = d_str
        # Small colored indicator line under button
        st.markdown(f"<div style='height:5px; background-color:{bg}; margin-top:-10px; border-radius:2px;'></div>", unsafe_allow_html=True)

st.divider()

# DAY VIEW
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today.strftime("%Y-%m-%d")

sel_date = st.session_state.selected_date
st.header(f"Day View: {sel_date}")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Add Specific Task")
    t_name = st.text_input("Single Task Name", key="single_t")
    if st.button("Add Task"):
        if sel_date not in data["daily_plans"]:
            data["daily_plans"][sel_date] = []
        data["daily_plans"][sel_date].append({"name": t_name, "done": False})
        save()
        st.rerun()

with col_right:
    st.subheader("Tasks for this Day")
    day_tasks = data["daily_plans"].get(sel_date, [])
    if not day_tasks:
        st.info("Nothing planned.")
    else:
        for i, task in enumerate(day_tasks):
            c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
            # Checkbox updates state immediately
            check = c1.checkbox("", value=task["done"], key=f"c_{sel_date}_{i}")
            if check != task["done"]:
                task["done"] = check
                save()
                st.rerun()
            
            label = f"~~{task['name']}~~" if task["done"] else task["name"]
            c2.markdown(label)
            
            if c3.button("🗑️", key=f"d_{sel_date}_{i}"):
                day_tasks.pop(i)
                save()
                st.rerun()
