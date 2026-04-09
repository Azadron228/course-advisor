import streamlit as st
import httpx
import os
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="University Course Advisor", layout="wide")
st.title("🎓 University Course Advisor")

# Sidebar for preferences
st.sidebar.header("User Preferences")
difficulty = st.sidebar.slider("Target Difficulty (0=Easy, 1=Hard)", 0.0, 1.0, 0.5)
workload = st.sidebar.slider("Max Workload (0=Low, 1=High)", 0.0, 1.0, 0.5)
interests = st.sidebar.text_input("Interests (comma separated)", "Python, AI, Data")

# Main area
st.subheader("1. Your Transcript")
transcript_html = st.text_area("Paste Transcript HTML here (from Platonus)", height=200)

if st.button("Get Recommendations"):
    if not transcript_html:
        st.error("Please paste your transcript HTML first.")
    else:
        with st.spinner("Analyzing your profile..."):
            try:
                # 1. Parse transcript
                parse_resp = httpx.post(f"{BACKEND_URL}/parse-transcript", json={"html": transcript_html})
                parse_resp.raise_for_status()
                transcript_entries = parse_resp.json()
                
                if not transcript_entries:
                    st.warning("No courses found in transcript. Please check the HTML.")
                else:
                    st.success(f"Parsed {len(transcript_entries)} courses from transcript.")
                    
                    # 2. Get recommendations
                    student_data = {
                        "id": "student_1",
                        "name": "User",
                        "transcript": transcript_entries,
                        "current_skills": [s.strip() for s in interests.split(",")]
                    }
                    pref_data = {
                        "interest_tags": [s.strip() for s in interests.split(",")],
                        "target_difficulty": difficulty,
                        "max_workload": workload
                    }
                    
                    rec_resp = httpx.post(
                        f"{BACKEND_URL}/recommend", 
                        params={"model_provider": model_provider},
                        json={"student": student_data, "preference": pref_data}, 
                        timeout=60.0 # Increased timeout for local LLM
                    )
                    rec_resp.raise_for_status()
                    recommendations = rec_resp.json()["results"]
                    
                    if not recommendations:
                        st.info("No course recommendations found. Make sure seed data is loaded in DB.")
                    else:
                        st.subheader("2. Recommended Courses")
                        for rec in recommendations:
                            with st.expander(f"{rec['subject_name']} (Score: {rec['score']:.2f})"):
                                st.write(f"**Reasoning:** {rec['reasoning']}")
                                st.write(f"**Tags:** {', '.join(rec['reason_tags'])}")
                                
                                # Show score breakdown
                                b = rec['breakdown']
                                df = pd.DataFrame({
                                    "Component": ["Content Similarity", "Skill Gap Coverage", "Preference Match", "RAG Reasoning"],
                                    "Score": [b['content_sim'], b['skill_gap'], b['preference'], b['rag_reasoning']]
                                })
                                st.table(df)
                                
            except Exception as e:
                st.error(f"Error communicating with backend: {e}")

st.divider()
st.caption("University Course Recommendation System powered by PydanticAI and pgvector.")
