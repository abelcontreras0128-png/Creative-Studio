import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Forward Planner", layout="wide")

# --- DATA HANDLING ---
DATA_FILE = "studio_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"projects": [], "daily_plans": {}}

data = load_data()

# Initialize empty keys if they don't exist
if "projects" not in data: data["projects"] = []
if "daily_plans" not in data: data["daily_plans"] = {}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- SIDEBAR: ADVANCED PROJECT BOARD ---
st.sidebar.title("📁 Project Board")

# 1. Add/Edit Projects
with st.sidebar.expander("✨ Manage Projects"):
    # Adding
    st.write("---")
    new_name = st.text_input("New Project Name")
    new_format = st.text_input("Custom Format (e.g. Script, Book)")
    if st.button("Add"):
        data["projects"].append({"name": new_name, "format": new_format, "status": "Parked", "stage": "Concept"})
        save()
        st.rerun()
    
    # Editing existing
    st.write("---")
    st.write("Edit Existing:")
    for i, p in enumerate(data["projects"]):
        with st.expander(f"Edit: {p['name']}"):
            p['name'] = st.text_input("Rename", value=p['name'], key=f"ren_{i}")
            p['format'] = st.text_input("Format", value=p['format'], key=f"form_{i}")
            if st.button("Delete Project", key=f"del_{i}"):
                data["projects"].pop(i)
                save()
                st.rerun()

# 2. Status Toggles
st.sidebar.subheader("Active (Max 3)")
active_p = [p for p in data["projects"] if p["status"] == "Active"]
for p in active_p:
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(f"**{p['name']}**")
    if col2.button("🅿️", key=f"park_{p['name']}"):
        p["status"] = "Parked"
        save()
        st.rerun()

st.sidebar.subheader("Parked Projects")
for p in [p for p in data["projects"] if p["status"] == "Parked"]:
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(p["name"])
    if col2.button("✅", key=f"act_{p['name']}"):
        if len(active_p) < 3:
            p["status"] = "Active"
            save()
            st.rerun()

# --- MAIN UI ---
st.title("📅 60-Day Forward Planner")

# 1. THE FORWARD GRID
today = datetime.now().date()
st.subheader("Upcoming 60 Days")

# Color Logic Function
def get_color(date_str):
    plan = data["daily_plans"].get(date_str, [])
    if not plan: return "gray"
    
    total = len(plan)
    done = sum(1 for t in plan if t.get("done", False))
    
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    if done == total and total > 0: return "green"
    if done > 0: return "orange"
    if date_obj < today and done == 0: return "red"
    return "#333" # Planned but not yet reached

# Display Grid
cols = st.columns(10)
for i in range(60):
    day = today + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    bg = get_color(d_str)
    
    with cols[i % 10]:
        if st.button(f"{day.month}/{day.day}", key=f"btn_{d_str}", use_container_width=True):
            st.session_state.selected_date = d_str

st.divider()

# 2. DAY INSPECTOR (The "Click a Day" feature)
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today.strftime("%Y-%m-%d")

sel_date = st.session_state.selected_date
st.header(f"Day View: {sel_date}")

# Add Tasks to the Day
with st.expander("➕ Add Task to this Day"):
    t_name = st.text_input("Task Description")
    if st.button("Add Task"):
        if sel_date not in data["daily_plans"]:
            data["daily_plans"][sel_date] = []
        data["daily_plans"][sel_date].append({"name": t_name, "done": False})
        save()
        st.rerun()

# Show Tasks for Selected Day
day_tasks = data["daily_plans"].get(sel_date, [])
if not day_tasks:
    st.info("No tasks planned for this day.")
else:
    for i, task in enumerate(day_tasks):
        col1, col2 = st.columns([0.1, 0.9])
        # Using checkboxes to toggle "Done"
        is_done = col1.checkbox("", value=task["done"], key=f"chk_{sel_date}_{i}")
        if is_done != task["done"]:
            task["done"] = is_done
            save()
            st.rerun()
        col2.write(f"~~{task['name']}~~" if is_done else task["name"])
        
        # Option to delete a specific task
        if st.button("🗑️", key=f"deltask_{i}"):
            day_tasks.pop(i)
            save()
            st.rerun()
