import streamlit as st
from google import genai
import requests
import re
import json
import os
import time

st.set_page_config(page_title="Rosetta Agent", page_icon="🗿", layout="centered")

st.title("🗿 Rosetta Agent")
st.write("---")

CONFIG_FILE = "rosetta_config.json"

# --- HELPER FUNCTIONS FOR STORAGE ---
def load_saved_credentials():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_credentials_to_disk(gemini_key, gl_token, proj_id):
    config_data = {
        "GEMINI_API_KEY": gemini_key,
        "GITLAB_TOKEN": gl_token,
        "GITLAB_PROJECT_ID": proj_id
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

saved_data = load_saved_credentials()

# --- SIDEBAR WORKSPACE ---
st.sidebar.title("🤖 Agent Control Panel")
st.sidebar.write("---")

st.sidebar.subheader("📁 Project Workspace")
init_project = saved_data.get("GITLAB_PROJECT_ID", "")
project_id = st.sidebar.text_input("🎯 Active GitLab Project ID", value=init_project)

if project_id:
    st.sidebar.success(f"🔒 Rosetta Locked onto ID: {project_id}")
else:
    st.sidebar.warning("⚠️ Awaiting Project ID")

st.sidebar.write("---")

with st.sidebar.expander("⚙️ Core App Setup & Authentication", expanded=not bool(saved_data)):
    st.caption("Enter your keys once below to lock them into Rosetta's local system memory.")
    init_gemini = saved_data.get("GEMINI_API_KEY", "")
    init_gitlab = saved_data.get("GITLAB_TOKEN", "")
    
    api_key = st.text_input("Gemini API Key", value=init_gemini, type="password")
    gitlab_token = st.text_input("GitLab Access Token", value=init_gitlab, type="password")
    
    if st.button("🔒 Save & Lock Credentials", use_container_width=True, type="primary"):
        save_credentials_to_disk(api_key, gitlab_token, project_id)
        st.success("Configuration securely saved to disk!")
        st.rerun()

# --- CORE AGENT PIPELINE ENGINE ---
def fetch_latest_failed_log(proj_id, token):
    try:
        headers = {"PRIVATE-TOKEN": token}
        url = f"https://gitlab.com/api/v4/projects/{proj_id}/jobs?scope=failed"
        res = requests.get(url, headers=headers)
        
        if res.status_code == 200 and res.json():
            latest_failed_job = res.json()[0]
            job_id = latest_failed_job["id"]
            
            trace_url = f"https://gitlab.com/api/v4/projects/{proj_id}/jobs/{job_id}/trace"
            trace_res = requests.get(trace_url, headers=headers)
            if trace_res.status_code == 200:
                return trace_res.text[-2000:] 
        return "No recent failed jobs found. Check your Project ID!"
    except Exception as e:
        return f"Error connecting to GitLab: {e}"

def push_fix_to_gitlab(proj_id, token, fixed_code):
    try:
        headers = {"PRIVATE-TOKEN": token}
        url = f"https://gitlab.com/api/v4/projects/{proj_id}/repository/files/app.py"
        payload = {
            "branch": "main",
            "commit_message": "🔧 Rosetta Agent: Automatically patched pipeline failure",
            "content": fixed_code
        }
        res = requests.put(url, headers=headers, json=payload)
        return res.status_code == 200
    except Exception as e:
        return False

def get_latest_pipeline_status(proj_id, token):
    try:
        headers = {"PRIVATE-TOKEN": token}
        url = f"https://gitlab.com/api/v4/projects/{proj_id}/pipelines"
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and res.json():
            return res.json()[0]["status"]
        return "unknown"
    except Exception:
        return "error"

# Interface States
if "current_log" not in st.session_state:
    st.session_state["current_log"] = "Click 'Fetch Live GitLab Log' to grab data."
if "ai_explanation" not in st.session_state:
    st.session_state["ai_explanation"] = ""
if "extracted_code" not in st.session_state:
    st.session_state["extracted_code"] = ""

# --- UPGRADED: BUTTON LOGIC WITH SMART PRE-CHECK ---
if st.sidebar.button("🔄 Fetch Live GitLab Log", use_container_width=True):
    if not project_id:
        st.sidebar.error("Please enter a Project ID first!")
    elif not gitlab_token:
        st.sidebar.error("Missing GitLab Access Token! Save it in Setup first.")
    else:
        with st.spinner("Analyzing project health status..."):
            # Inspect the absolute newest event on the repository
            latest_status = get_latest_pipeline_status(project_id, gitlab_token)
            
            if latest_status == "success":
                # Clear everything out clean if the pipeline is already healthy
                st.session_state["current_log"] = "🎉 Everything is passing perfectly! The latest cloud build is completely healthy. No errors to heal."
                st.session_state["ai_explanation"] = ""
                st.session_state["extracted_code"] = ""
            else:
                # If it's failed, pending, or running, grab the logs to investigate
                st.session_state["current_log"] = fetch_latest_failed_log(project_id, gitlab_token)

st.subheader("❌ Retrieved Pipeline Failure Trace")
st.code(st.session_state["current_log"], language="text")

if st.button("✨ Decipher with Rosetta", type="primary"):
    # Prevent Rosetta from analyzing the "Success" confirmation string
    if "Everything is passing perfectly!" in st.session_state["current_log"]:
        st.info("The repository is completely clean. No debugging action is required!")
    elif not api_key:
        st.error("Missing Gemini API Key! Save it in Setup first.")
    else:
        with st.spinner("Analyzing crash sequence..."):
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                You are Rosetta Agent. Analyze this raw pipeline error trace and provide exactly two things:
                1. A brief, plain-English explanation of why the build failed.
                2. The FULL corrected python file (app.py) wrapped inside a single ```python ``` block. Do not use excerpts.
                
                Log Trace:
                {st.session_state['current_log']}
                """
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                raw_text = response.text
                st.session_state["ai_explanation"] = raw_text
                
                code_blocks = re.findall(r"```python\s*(.*?)\s*```", raw_text, re.DOTALL)
                if code_blocks:
                    st.session_state["extracted_code"] = code_blocks[0]
                else:
                    st.session_state["extracted_code"] = "# Could not auto-parse code."
                    
            except Exception as e:
                st.error(f"AI Connection Error: {e}")

if st.session_state["ai_explanation"]:
    st.write("---")
    st.subheader("💡 Rosetta Analysis")
    st.markdown(st.session_state["ai_explanation"])
    
    st.write("---")
    st.subheader("🛠️ Interactive Auto-Heal Deployment")
    
    final_code_to_push = st.text_area("Review Code to Commit:", value=st.session_state["extracted_code"], height=150)
    
    if st.button("🚀 Auto-Apply Patch & Push to GitLab", type="primary"):
        with st.spinner("Committing changes directly to GitLab via API..."):
            success = push_fix_to_gitlab(project_id, gitlab_token, final_code_to_push)
            
            if success:
                st.success("🔥 Code successfully injected into GitLab Repository!")
                
                st.write("---")
                st.subheader("📊 Live CI/CD Pipeline Monitor")
                
                monitor_box = st.empty()
                monitor_box.info("⏳ Waiting for GitLab to initialize new runner sequence...")
                
                for cycle in range(30):
                    time.sleep(4)
                    current_status = get_latest_pipeline_status(project_id, gitlab_token)
                    
                    if current_status == "running":
                        monitor_box.info("⚙️ Pipeline Status: **RUNNING** — Actively evaluating your patch code...")
                    elif current_status == "success":
                        monitor_box.success("🎉 Pipeline Status: **PASSED**! Rosetta successfully healed the cloud build!")
                        st.balloons()
                        break
                    elif current_status == "failed":
                        monitor_box.error("❌ Pipeline Status: **FAILED**. The patch did not satisfy the compilation criteria.")
                        break
                    elif current_status == "pending":
                        monitor_box.warning("⏳ Pipeline Status: **PENDING** — Stuck in queue. Awaiting runner environment...")
                    elif current_status == "canceled":
                        monitor_box.error("🚫 Pipeline Status: **CANCELED** — The deployment sequence was aborted manually.")
                        break
                    else:
                        monitor_box.write(f"🔍 Pipeline Status: **{current_status.upper()}**")
            else:
                st.error("Failed to push. Verify your main branch isn't completely locked or protected.")