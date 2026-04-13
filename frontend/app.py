import streamlit as st
import httpx
import os
import pandas as pd
import json
from datetime import datetime

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Course Advisor | AI-Powered Recommendations", 
    page_icon="🎓", 
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .recommendation-card { padding: 1.5rem; border-radius: 10px; border-left: 5px solid #007bff; background-color: white; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .score-badge { background-color: #e7f3ff; color: #007bff; padding: 0.2rem 0.6rem; border-radius: 20px; font-weight: bold; float: right; }
    .auth-container { max-width: 400px; margin: 0 auto; padding: 2rem; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

def login(username, password):
    try:
        resp = httpx.post(
            f"{BACKEND_URL}/token",
            data={"username": username, "password": password}
        )
        if resp.status_code == 200:
            st.session_state.token = resp.json()["access_token"]
            st.session_state.username = username
            return True
        else:
            st.error(f"Login failed: {resp.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Connection error: {e}")
        return False

def register(username, password, email, full_name):
    try:
        resp = httpx.post(
            f"{BACKEND_URL}/register",
            json={"username": username, "password": password, "email": email, "full_name": full_name}
        )
        if resp.status_code == 200:
            st.success("Registration successful! Please log in.")
            return True
        else:
            st.error(f"Registration failed: {resp.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Connection error: {e}")
        return False

def logout():
    st.session_state.token = None
    st.session_state.username = None
    st.rerun()

# --- Authentication View ---
if not st.session_state.token:
    st.title("🎓 AI Course Advisor")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.container():
            st.subheader("Welcome Back")
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if login(login_user, login_pass):
                    st.rerun()
                    
    with tab2:
        with st.container():
            st.subheader("Create Account")
            reg_user = st.text_input("Username", key="reg_user")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            reg_full = st.text_input("Full Name")
            reg_email = st.text_input("Email")
            if st.button("Register"):
                register(reg_user, reg_pass, reg_email, reg_full)
    st.stop()

# --- Main Application View (Authenticated) ---
st.title("🎓 AI Course Advisor")
st.markdown(f"Welcome, **{st.session_state.username}**!")

# Sidebar
with st.sidebar:
    st.header("👤 Profile")
    st.write(f"Logged in as: {st.session_state.username}")
    if st.button("Logout"):
        logout()
    
    st.divider()
    st.header("🎯 Your Goals")
    difficulty = st.slider("Target Difficulty", 0.0, 1.0, 0.5)
    workload = st.slider("Max Workload", 0.0, 1.0, 0.5)
    
    st.divider()
    st.header("🔍 Interests & Skills")
    interests_str = st.text_area("What are you interested in?", "Machine Learning, Web Development", height=100)
    interests = [s.strip() for s in interests_str.split(",") if s.strip()]

    st.divider()
    st.header("📄 Academic History")
    uploaded_file = st.file_uploader("Upload Platonus Transcript (HTML)", type=["html"])

headers = {"Authorization": f"Bearer {st.session_state.token}"}

if st.button("🚀 Generate Personalized Recommendations"):
    if not uploaded_file:
        st.error("Please upload your transcript HTML file.")
    elif not interests:
        st.error("Please enter at least one interest.")
    else:
        with st.spinner("🧠 Analyzing and matching..."):
            try:
                # 1. Parse transcript
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/html")}
                parse_resp = httpx.post(f"{BACKEND_URL}/parse-transcript", files=files, headers=headers)
                
                if parse_resp.status_code == 401:
                    st.error("Session expired. Please log in again.")
                    logout()
                
                if parse_resp.status_code != 200:
                    st.error(f"Error parsing: {parse_resp.text}")
                    st.stop()
                
                transcript_entries = parse_resp.json()
                
                if not transcript_entries:
                    st.warning("No courses detected.")
                else:
                    st.info(f"Analyzed academic history: **{len(transcript_entries)}** courses.")
                    
                    # 2. Get recommendations
                    student_data = {
                        "id": st.session_state.username,
                        "name": st.session_state.username,
                        "transcript": transcript_entries,
                        "current_skills": interests
                    }
                    pref_data = {
                        "interest_tags": interests,
                        "target_difficulty": difficulty,
                        "max_workload": workload
                    }
                    
                    rec_resp = httpx.post(
                        f"{BACKEND_URL}/recommend", 
                        json={"student": student_data, "preference": pref_data}, 
                        headers=headers,
                        timeout=120.0 # Increased for global analysis
                    )
                    
                    if rec_resp.status_code == 401:
                        st.error("Session expired.")
                        logout()

                    if rec_resp.status_code != 200:
                        st.error(f"Error: {rec_resp.text}")
                        st.stop()
                        
                    data = rec_resp.json()
                    recommendations = data.get("results", [])
                    analysis = data.get("skill_gap_analysis")
                    path = data.get("learning_path", [])
                    
                    # --- Analysis Results ---
                    if analysis:
                        st.divider()
                        st.header("📊 Your Skill Gap Analysis")
                        
                        col_a, col_b = st.columns([1, 2])
                        with col_a:
                            st.metric("Overall Gap Score", f"{analysis['overall_gap_score']:.2f}")
                            st.write("**Critical Skills Missing:**")
                            for skill in analysis.get('critical_skills', []):
                                st.error(f"缺失: {skill}")
                        
                        with col_b:
                            st.write("**Gap Score by Domain:**")
                            for domain in analysis.get('domain_breakdown', []):
                                st.progress(domain['gap_score'], text=f"{domain['domain']}: {domain['gap_score']:.2f}")
                                with st.expander(f"See missing {domain['domain']} skills"):
                                    st.write(", ".join(domain.get('missing_skills', [])))

                    # --- Learning Path ---
                    if path:
                        st.divider()
                        st.header("🗺️ Recommended Learning Path")
                        for step in sorted(path, key=lambda x: x['order']):
                            with st.chat_message("user" if step['order'] % 2 == 0 else "assistant"):
                                st.write(f"**Step {step['order']}: {step['title']}**")
                                st.write(step['description'])
                                if step.get('resource_id'):
                                    if step.get('is_external'):
                                        st.link_button("🌐 External Resource", step['resource_id'])
                                    else:
                                        st.info(f"📍 Course ID: {step['resource_id']}")

                    # --- Recommendations ---
                    if not recommendations:
                        st.warning("No matches found.")
                    else:
                        st.divider()
                        st.header("🔝 Top Recommended Courses")
                        for idx, rec in enumerate(recommendations):
                            score_val = rec.get('score', 0.0)
                            score_pct = score_val * 100
                            with st.container():
                                st.markdown(f"""
                                    <div class="recommendation-card">
                                        <span class="score-badge">{score_pct:.1f}% Match</span>
                                        <h3 style="margin-top:0;">{idx+1}. {rec['subject_name']}</h3>
                                        <p><strong>Why this fits:</strong> {rec['reasoning']}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    for tag in rec.get('reason_tags', []):
                                        st.markdown(f"✅ {tag}")
                                with col2:
                                    b = rec.get('breakdown', {})
                                    metrics = {
                                        "Academic Alignment": b.get('content_sim', 0.0),
                                        "Skill Gap Coverage": b.get('skill_gap', 0.0),
                                        "Interest Match": b.get('preference', 0.0),
                                        "AI Reasoning Confidence": b.get('rag_reasoning', 0.0)
                                    }
                                    for m_name, m_val in metrics.items():
                                        val = float(m_val) if m_val is not None else 0.0
                                        st.progress(val, text=f"{m_name}: {val:.2f}")
                                st.divider()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
else:
    col1, col2, col3 = st.columns(3)
    with col1: st.info("📂 **Upload**\nUpload your transcript to begin.")
    with col2: st.success("🎯 **Set Goals**\nDefine your interests and difficulty.")
    with col3: st.warning("💡 **Get Advice**\nGet RAG-powered course recommendations.")

st.sidebar.markdown("---")
st.sidebar.caption("v2.1 Secured | Powered by PydanticAI & pgvector")
