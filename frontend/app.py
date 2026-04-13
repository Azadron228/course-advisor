import streamlit as st
import httpx
import os
import pandas as pd
import json

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Course Advisor | AI-Powered Recommendations", 
    page_icon="🎓", 
    layout="wide"
)

# Custom CSS for a more modern look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .recommendation-card {
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        background-color: white;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .score-badge {
        background-color: #e7f3ff;
        color: #007bff;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-weight: bold;
        float: right;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 AI Course Advisor")
st.markdown("Discover the perfect courses tailored to your academic history and professional goals.")

# Layout: Sidebar for Preferences and File Upload
with st.sidebar:
    st.header("🎯 Your Goals")
    difficulty = st.slider("Target Difficulty", 0.0, 1.0, 0.5, help="0 = Easy-going, 1 = Academic challenge")
    workload = st.slider("Max Workload", 0.0, 1.0, 0.5, help="0 = Light, 1 = Intensive")
    
    st.divider()
    st.header("🔍 Interests & Skills")
    interests_str = st.text_area("What are you interested in?", "Machine Learning, Web Development, Russian History", height=100)
    interests = [s.strip() for s in interests_str.split(",") if s.strip()]

    st.divider()
    st.header("📄 Academic History")
    uploaded_file = st.file_uploader("Upload Platonus Transcript (HTML)", type=["html"])

# Main Area
if st.button("🚀 Generate Personalized Recommendations"):
    if not uploaded_file:
        st.error("Please upload your transcript HTML file to proceed.")
    elif not interests:
        st.error("Please enter at least one interest or target skill.")
    else:
        with st.spinner("🧠 Analyzing your academic profile and matching with courses..."):
            try:
                # 1. Parse transcript using the new UploadFile endpoint
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/html")}
                parse_resp = httpx.post(f"{BACKEND_URL}/parse-transcript", files=files)
                
                if parse_resp.status_code != 200:
                    st.error(f"Failed to parse transcript: {parse_resp.text}")
                    st.stop()
                
                transcript_entries = parse_resp.json()
                
                if not transcript_entries:
                    st.warning("No courses detected in the uploaded file. Please ensure it's a valid Platonus transcript.")
                else:
                    st.info(f"Successfully analyzed academic history: **{len(transcript_entries)}** courses completed.")
                    
                    # 2. Get recommendations
                    student_data = {
                        "id": "student_current",
                        "name": "Academic User",
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
                        timeout=90.0 # High timeout for RAG + LLM processing
                    )
                    
                    if rec_resp.status_code != 200:
                        st.error(f"Recommendation engine error: {rec_resp.text}")
                        st.stop()
                        
                    recommendations = rec_resp.json()["results"]
                    
                    if not recommendations:
                        st.warning("We couldn't find any courses matching your criteria in our catalog.")
                        st.button("Try adjusting your preferences")
                    else:
                        st.success("Found your top matches!")
                        
                        for idx, rec in enumerate(recommendations):
                            score_val = rec.get('score')
                            if score_val is None:
                                # Fallback or debug
                                st.warning(f"Warning: Score missing for course {rec.get('subject_name')}")
                                score_val = 0.0
                                
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
                                    st.write("**Recommended because:**")
                                    for tag in rec['reason_tags']:
                                        st.markdown(f"✅ {tag}")
                                
                                with col2:
                                    # Visual score breakdown
                                    b = rec.get('breakdown', {})
                                    metrics = {
                                        "Academic Alignment": b.get('content_sim', 0.0),
                                        "Skill Gap Coverage": b.get('skill_gap', 0.0),
                                        "Interest Match": b.get('preference', 0.0),
                                        "AI Reasoning Confidence": b.get('rag_reasoning', 0.0)
                                    }
                                    st.write("**Matching Breakdown:**")
                                    for m_name, m_val in metrics.items():
                                        # Safe cast to float to prevent TypeError: unsupported format string passed to NoneType.__format__
                                        val = float(m_val) if m_val is not None else 0.0
                                        st.progress(val, text=f"{m_name}: {val:.2f}")
                                
                                st.divider()

            except httpx.ConnectError:
                st.error("Could not connect to the backend server. Is it running at " + BACKEND_URL + "?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                st.exception(e)

else:
    # Landing page state
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📂 **Upload**\nUpload your Platonus transcript to let the AI understand your foundation.")
    with col2:
        st.success("🎯 **Set Goals**\nDefine your interests and how hard you want to push yourself.")
    with col3:
        st.warning("💡 **Get Advice**\nOur RAG-powered engine finds the best courses for your career path.")

st.sidebar.markdown("---")
st.sidebar.caption("v2.0 Refactored | Powered by PydanticAI & pgvector")
