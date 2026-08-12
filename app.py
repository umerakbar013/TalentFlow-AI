import streamlit as st
import datetime
import json
import base64
from pathlib import Path

from schemas.recruitment_state import ComplianceConsent, ApplicationStage
from utils.audio_processor import save_candidate_audio, transcribe_audio
from utils.document_generator import generate_offer_letter, extract_text_from_pdf
from agents.screening_agent import ScreeningAgent
from agents.interview_agent import DynamicInterviewerAgent
from agents.negotiation_agent import SalaryNegotiationEngine

st.set_page_config(page_title="TalentFlow AI", layout="wide")

# --- ENTERPRISE UI CSS INJECTION ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    h1 { color: #00E5FF; font-weight: 800; letter-spacing: -1px; border-bottom: 1px solid #1A2235; padding-bottom: 1rem; }
    div.stButton > button:first-child { background-color: #1A2235; color: #FFFFFF; border: 1px solid #00E5FF; border-radius: 6px; padding: 0.5rem 1rem; font-weight: 600; transition: all 0.3s ease; }
    div.stButton > button:hover { background-color: #00E5FF; color: #0B0F19; border: 1px solid #00E5FF; box-shadow: 0 0 10px rgba(0, 229, 255, 0.4); }
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #1A2235; }
    div.stAlert { border-radius: 6px; border-left: 4px solid; }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "consent" not in st.session_state:
    st.session_state.consent = ComplianceConsent()
if "stage" not in st.session_state:
    st.session_state.stage = ApplicationStage.SCREENING
if "interviewer" not in st.session_state:
    st.session_state.interviewer = DynamicInterviewerAgent("Sample Resume Context")
if "negotiator" not in st.session_state:
    st.session_state.negotiator = SalaryNegotiationEngine()
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = "Umer Akbar"
if "question_count" not in st.session_state:
    st.session_state.question_count = 1

st.title("TalentFlow AI — Operations Engine")

# --- PHASE 1: FULLY AUTOMATED ATS FOLDER SCAN ---
if st.session_state.stage == ApplicationStage.SCREENING:
    st.subheader("Phase 1: Automated ATS Folder Scan")
    st.write("Automatically processing all candidate files located in the company ATS directory (`data/sample_resumes/`).")
    
    if "leaderboard_data" not in st.session_state:
        st.session_state.leaderboard_data = None
        st.session_state.top_candidate_data = None
    
    department = st.selectbox(
        "Select Target Department Template", 
        ["Software Development", "Finance", "Civil Engineering", "Aerospace", "Marketing"]
    )
    
    sample_jds = {
        "Software Development": "Requirements: Python, FastAPI, PyTorch. Experience with multi-agent system architecture, vector databases, and RAG pipelines.",
        "Finance": "Requirements: Financial modeling, corporate valuation, balance sheet risk analysis.",
        "Civil Engineering": "Requirements: AutoCAD, structural analysis, project management.",
        "Aerospace": "Requirements: Aerodynamics, propulsion systems, flight mechanics.",
        "Marketing": "Requirements: SEO, digital marketing strategy, content creation."
    }

    custom_jd = st.text_area("Target Job Description", value=sample_jds[department], height=100)

    if st.button("Start Automated Batch Scan"):
        resume_dir = Path("data/sample_resumes")
        pdf_files = list(resume_dir.glob("*.pdf"))
        
        if not pdf_files:
            st.warning("No PDF resumes found! Please ensure files are in `data/sample_resumes/`.")
        else:
            st.info(f"System detected {len(pdf_files)} resumes. Commencing AI evaluation pipeline...")
            leaderboard = []
            agent = ScreeningAgent(job_description=custom_jd, target_department=department)
            progress_bar = st.progress(0)
            
            for index, file_path in enumerate(pdf_files):
                with open(file_path, "rb") as f:
                    pdf_bytes = f.read()
                resume_text = extract_text_from_pdf(pdf_bytes)
                result = agent.evaluate_resume(resume_text)
                
                leaderboard.append({
                    "Candidate Name": file_path.stem.replace("_", " ").title(),
                    "Score": result["score"],
                    "Status": "Passed" if result["passed"] else "Rejected",
                    "Feedback": result["feedback"]
                })
                progress_bar.progress((index + 1) / len(pdf_files))
            
            st.session_state.leaderboard_data = leaderboard
            passed_candidates = [c for c in leaderboard if c["Status"] == "Passed"]
            if passed_candidates:
                st.session_state.top_candidate_data = sorted(passed_candidates, key=lambda x: x["Score"], reverse=True)[0]
            else:
                st.session_state.top_candidate_data = None

    if st.session_state.leaderboard_data is not None:
        st.write("### AI Screening Leaderboard")
        st.dataframe(st.session_state.leaderboard_data, use_container_width=True)
        
        if st.session_state.top_candidate_data:
            candidate_name = "Umer Akbar"
            formatted_email = "umer.akbar@inventacore.ai"
            st.success(f"**Top Candidate Detected:** {candidate_name} (Score: {st.session_state.top_candidate_data['Score']}). Triggering automated email dispatch...")
            
            st.markdown("---")
            st.subheader("📬 Candidate Email Inbox (Simulation)")
            
            st.info(
                f"**From:** talent.acquisition@inventacore.ai\n\n"
                f"**To:** {formatted_email}\n\n"
                f"**Subject: Invitation to Technical Assessment – Agentic AI Engineer**\n\n"
                f"---\n\n"
                f"Dear {candidate_name},\n\n"
                f"Thank you for your application to the Agentic AI Engineer position at Inventacore. Our autonomous screening systems have completed a preliminary review of your credentials. We were highly impressed by your technical background, specifically your experience with multi-agent frameworks and API architectures.\n\n"
                f"We would like to officially invite you to the next stage of our recruitment process: a live, AI-driven technical assessment.\n\n"
                f"This interactive voice session is designed to evaluate your system design capabilities, problem-solving skills, and practical engineering knowledge in real-time. Please ensure you are in a quiet environment and have a working microphone before proceeding.\n\n"
                f"Click the secure portal link below when you are ready to begin your session.\n\n"
                f"Best regards,\n\n"
                f"**Talent Acquisition Team**\n"
                f"Inventacore Autonomous Operations Engine"
            )
            
            if st.button("🔗 CLICK HERE TO START INTERVIEW (portal.inventacore.ai/session=active)"):
                st.session_state.candidate_name = candidate_name
                st.session_state.stage = ApplicationStage.CONSENT_GATE
                st.session_state.leaderboard_data = None 
                st.rerun()

# --- PHASE 2: CONSENT GATE ---
elif st.session_state.stage == ApplicationStage.CONSENT_GATE:
    st.subheader("Phase 2: Compliance & Privacy Authorization")
    st.info("To proceed, you must consent to the AI recording and transcribing your audio for HR verification.")
    
    consent_check = st.checkbox("I agree to the recording and processing of my interview.")
    
    if st.button("Proceed to Interview Room", disabled=not consent_check):
        st.session_state.consent.consent_given = True
        st.session_state.consent.timestamp = datetime.datetime.now().isoformat()
        st.session_state.stage = ApplicationStage.INTERVIEW
        st.session_state.current_q = st.session_state.interviewer.generate_first_question()
        st.rerun()

# --- PHASE 3: INTERVIEW (SIMULATED REAL-TIME VOICE) ---
elif st.session_state.stage == ApplicationStage.INTERVIEW:
    col1, col2 = st.columns([2, 1])
    
    # Force exactly 3 specific questions for the demo
    demo_questions = [
        "I see your repository features multi-agent frameworks. Walk me through how you handle memory across turns.",
        "Great. How do you implement guardrails against prompt injection in your RAG pipelines?",
        "Finally, what specific metrics did you use to measure the success of your last deployed model?"
    ]
    
    # Ensure current question matches the turn count safely
    q_index = min(st.session_state.question_count - 1, 2)
    st.session_state.current_q = demo_questions[q_index]
        
    with col1:
        st.subheader("Phase 3: Live Interview Room")
        
        # Generate AI Voice
        from gtts import gTTS
        tts = gTTS(st.session_state.current_q, lang='en')
        tts.save("agent_voice.mp3")
        with open("agent_voice.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            
        st.write(f"**Agent Question {st.session_state.question_count}/3:** {st.session_state.current_q}")
        
        import streamlit.components.v1 as components
        components.html(f"""
            <audio id="ai_audio" autoplay="true" src="data:audio/mp3;base64,{b64}"></audio>
            <div id="timer_box" style="font-family: sans-serif; color: #64748b; font-size: 18px; font-weight: bold; background: #1A2235; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #334155; transition: all 0.3s;">
                ⏳ AI is speaking... waiting for microphone...
            </div>
            <script>
                var audio = document.getElementById('ai_audio');
                var timerBox = document.getElementById('timer_box');
                var timeLeft = 60;
                var timerId;

                audio.onended = function() {{
                    timerBox.style.color = "#00E5FF";
                    timerBox.style.borderColor = "#00E5FF";
                    timerBox.innerHTML = "⏱️ Auto-Submit Timer: <span id='time'>60</span> Seconds";
                    timerId = setInterval(countdown, 1000);
                }};

                function countdown() {{
                    var elem = document.getElementById('time');
                    if (timeLeft <= 0) {{
                        clearTimeout(timerId);
                        elem.innerHTML = "0 (Recording Locked)";
                        timerBox.style.borderColor = "#FF004D";
                        timerBox.style.color = "#FF004D";
                    }} else {{
                        timeLeft--;
                        elem.innerHTML = timeLeft;
                    }}
                }}
            </script>
        """, height=90)
        
        # Reset microphone widget every turn
        audio_val = st.audio_input("Press microphone to answer (Timer starts after AI finishes)", key=f"mic_turn_{st.session_state.question_count}")
        
        if audio_val:
            bytes_data = audio_val.read()
            audio_path = save_candidate_audio(bytes_data, st.session_state.candidate_name.replace(" ", "_"), st.session_state.question_count)
            
            transcript = transcribe_audio(bytes_data)
            st.success(f"**You said:** {transcript}")
            
            st.session_state.audit_log.append({
                "turn": st.session_state.question_count, 
                "transcript": transcript, 
                "audio_path": audio_path
            })
            
            st.session_state.question_count += 1
            
            if st.session_state.question_count <= 3:
                st.rerun()
            else:
                st.session_state.stage = ApplicationStage.NEGOTIATION
                st.rerun()
                
    with col2:
        st.subheader("Compliance Log")
        st.json(st.session_state.audit_log)

# --- PHASE 4: NEGOTIATION ---
elif st.session_state.stage == ApplicationStage.NEGOTIATION:
    st.subheader("Phase 4: Salary Negotiation Engine")
    st.write("You passed the technical screen. Let's discuss compensation.")
    demand = st.number_input("Enter Expected Salary ($)", min_value=50000, max_value=150000, value=85000, step=1000)
    
    if st.button("Submit Proposal"):
        result = st.session_state.negotiator.process_demand(demand)
        st.write(f"**Agent Response:** {result['msg']}")
        
        if result["action"] == "ACCEPT":
            pdf_path = generate_offer_letter(st.session_state.candidate_name, result["amount"])
            
            st.session_state.final_salary = result["amount"]
            st.session_state.offer_pdf = pdf_path
            
            with open("data/audit_db.json", "w") as f:
                json.dump(st.session_state.audit_log, f, indent=4)
                
            st.session_state.stage = ApplicationStage.OFFER_ISSUED
            st.rerun()

# --- PHASE 5: FINAL HR REPORT & ONSITE INVITATION ---
elif st.session_state.stage == ApplicationStage.OFFER_ISSUED:
    st.subheader("Phase 5: HR Dossier & Final Decision")
    
    # Initialize final score and HR decision state
    if "final_score" not in st.session_state:
        # Simulating a high passing score for your demo presentation
        st.session_state.final_score = 94 
        
    if "hr_decision" not in st.session_state:
        st.session_state.hr_decision = None

    st.write("### 📊 Candidate Evaluation Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Selected Candidate", st.session_state.candidate_name)
    col2.metric("Overall AI Score", f"{st.session_state.final_score}/100")
    col3.metric("Agreed Compensation", f"${st.session_state.final_salary:,.2f}")

    st.write("#### Interview Transcript & Scoring")
    for log in st.session_state.audit_log:
        st.info(f"**Turn {log['turn']} Answer Recorded:** \n\n*Transcript:* {log['transcript']}")

    st.markdown("---")
    
    # --- HR HUMAN-IN-THE-LOOP GATE ---
    # --- HR HUMAN-IN-THE-LOOP GATE ---
    if st.session_state.hr_decision is None:
        st.warning("⚠️ **Final Decision for Onsite Round:** Review the transcript dossier above to approve or reject the candidate for the onsite interview.")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ Approve Candidate", use_container_width=True):
                st.session_state.hr_decision = "Approved"
                st.rerun()
        with col_b:
            if st.button("❌ Reject Candidate", use_container_width=True):
                st.session_state.hr_decision = "Rejected"
                st.rerun()
                
    # --- POST-DECISION LOGIC ---
    elif st.session_state.hr_decision == "Approved":
        st.success(f"✅ Candidate Approved by HR. Overall Score: {st.session_state.final_score}/100.")
        
        # Only send the onsite invitation if the score is > 90
        if st.session_state.final_score > 90:
            st.subheader("📬 Final HR Outreach (Simulation)")
            formatted_email = st.session_state.candidate_name.replace(" ", ".").lower() + "@inventacore.ai"

            st.info(
                f"**From:** hr.director@inventacore.ai\n\n**To:** {formatted_email}\n\n"
                f"**Subject:** Congratulations! Final Onsite Meeting Invitation\n\n"
                f"Dear {st.session_state.candidate_name},\n\n"
                f"Congratulations! We are thrilled to inform you that you have successfully passed the AI Technical Interview and Salary Negotiation phases with an outstanding score of {st.session_state.final_score}/100.\n\n"
                f"The Operations Engine has generated your contract (attached as `{st.session_state.offer_pdf}`), and our HR team has reviewed your exceptional performance summary.\n\n"
                f"We would love to invite you to our office for a final onsite meeting to meet the engineering team, finalize your paperwork, and officially welcome you.\n\n"
                f"Best regards,\n\n**Human Resources Director**\nInventaCore"
            )
        else:
            st.info("Candidate approved, but score did not meet the 90+ threshold for an expedited onsite interview. Proceeding with standard remote onboarding.")
            
    elif st.session_state.hr_decision == "Rejected":
        st.error("❌ Candidate Rejected by HR. The recruitment pipeline has been safely terminated and no offer email was dispatched.")