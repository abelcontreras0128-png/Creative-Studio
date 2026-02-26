import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Creative Studio", layout="wide")

# --- DATA HANDLING ---
DATA_FILE = "studio_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"logs": {}, "projects": [], "tasks": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# --- SIDEBAR: PROJECT MANAGEMENT ---
st.sidebar.title("📁 Project Board")
with st.sidebar.expander("Add New Project"):
    new_p_name = st.text_input("Project Name")
    new_p_format = st.selectbox("Format", ["Novel", "Film Script", "TV Series", "Short Film"])
    if st.button("Add Project"):
        data["projects"].append({"name": new_p_name, "format": new_p_format, "status": "Parked", "stage": "Concept"})
        save_data(data)
        st.rerun()

st.sidebar.subheader("Active Projects")
active_projects = [p for p in data["projects"] if p["status"] == "Active"]
for i, p in enumerate(active_projects):
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(f"**{p['name']}** ({p['stage']})")
    if col2.button("🅿️", key=f"park_{i}"):
        p["status"] = "Parked"
        save_data(data)
        st.rerun()

st.sidebar.subheader("Parked")
parked_projects = [p for p in data["projects"] if p["status"] == "Parked"]
for i, p in enumerate(parked_projects):
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(p["name"])
    if col2.button("✅", key=f"act_{i}"):
        if len(active_projects) < 3:
            p["status"] = "Active"
            save_data(data)
            st.rerun()
        else:
            st.sidebar.error("Max 3 Active!")

# --- MAIN UI ---
st.title("🚀 Creative Studio: Daily Call-In")

# 1. THE 60-DAY GRID
st.subheader("Visual Progress (Last 60 Days)")
cols = st.columns(10)
today = datetime.now().date()
for i in range(60):
    day = today - timedelta(days=59-i)
    day_str = day.strftime("%Y-%m-%d")
    status = data["logs"].get(day_str, {}).get("status", "⚪")
    color_map = {"🟢": "green", "🟡": "orange", "🔴": "red", "⚪": "gray"}
    cols[i % 10].markdown(f"<div style='text-align:center; background-color:{color_map[status]}; padding:10px; border-radius:5px; margin:2px; color:white;'>{day.day}</div>", unsafe_allow_html=True)

st.divider()

# 2. CALL-IN SECTION
st.subheader("Log Your Shift")
c1, c2, c3 = st.columns(3)
with c1:
    shift_status = st.selectbox("How was today?", ["🟢 Completed (1-3hrs)", "🟡 Partial/Maintenance", "🔴 Missed"])
with c2:
    working_on = st.selectbox("Project", [p["name"] for p in active_projects] + ["None"])
with c3:
    next_step = st.text_input("Breadcrumb: Start tomorrow with...")

if st.button("Submit Call-In"):
    status_icon = shift_status[0]
    data["logs"][today.strftime("%Y-%m-%d")] = {"status": status_icon, "project": working_on, "next": next_step}
    save_data(data)
    st.success("Shift logged!")
    st.rerun()

st.divider()

# 3. DAILY TASKS (IRL & CREATIVE)
st.subheader("📋 Tasks & Commitments")
new_task = st.text_input("Add task (e.g. Doctor 2pm, B-day, Write 2 pages)")
if st.button("Add Task"):
    data["tasks"].append({"task": new_task, "done": False, "date": today.strftime("%Y-%m-%d")})
    save_data(data)
    st.rerun()

for i, t in enumerate(data["tasks"]):
    # Show all tasks for the current month/view as requested
    is_done = st.checkbox(f"{t['task']} ({t['date']})", value=t["done"], key=f"task_{i}")
    if is_done != t["done"]:
        t["done"] = is_done
        save_data(data)
