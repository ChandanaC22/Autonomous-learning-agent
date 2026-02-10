import streamlit as st
import os
from agent import app as agent_app
from models import Checkpoint, MCQ
from search_utils import search_for_simple_explanation
from context_utils import generate_feynman_explanation

# --- Page Configuration ---
st.set_page_config(
    page_title="Autonomous Learning Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styles ---
st.markdown("""
<style>
    .main-title { font-size: 2.8rem; font-weight: 700; color: #1E88E5; margin-bottom: 0.5rem; }
    .sub-title { font-size: 1.1rem; color: #666; margin-bottom: 2rem; }
    .stButton>button { border-radius: 8px; font-weight: 600; padding: 0.5rem; border: 1px solid #1E88E5; background: transparent; color: #1E88E5; }
    .stButton>button:hover { background-color: #1E88E5; color: white; }
    .summary-card { padding: 30px; background: #f8fbff; border-radius: 15px; border-left: 8px solid #1E88E5; box-shadow: inset 0 0 10px rgba(30, 136, 229, 0.05); color: #2c3e50; line-height: 1.7; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None
if "step" not in st.session_state:
    st.session_state.step = "input" # input, learning, quiz, complete
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "missed_indices" not in st.session_state:
    st.session_state.missed_indices = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "remediation_index" not in st.session_state:
    st.session_state.remediation_index = 0
if "seen_questions" not in st.session_state:
    st.session_state.seen_questions = []

# --- Sidebar ---
with st.sidebar:
    st.title("🗺️ Mastery Dashboard")
    
    # 1. Progress Overview
    step_flow = ["input", "learning", "quiz", "remediation", "complete"]
    step_labels = {
        "input": "🎯 Selection",
        "learning": "📖 Study",
        "quiz": "📝 Practice",
        "remediation": "🚀 Review",
        "complete": "🏆 Results"
    }
    
    try:
        progress_val = (step_flow.index(st.session_state.step) + 1) / len(step_flow)
    except:
        progress_val = 0.0
    st.progress(progress_val)
    st.caption(f"Overall Progress: {int(progress_val*100)}%")
    
    st.divider()

    # 2. Interactive Navigation (Journey Map)
    st.markdown("### 🧭 Navigation")
    state = st.session_state.agent_state
    
    for sid in step_flow:
        label = step_labels[sid]
        
        # Determine if step is "unlocked"
        is_current = st.session_state.step == sid
        is_unlocked = False
        
        if sid == "input":
            is_unlocked = True
        elif sid == "learning":
            is_unlocked = state is not None
        elif sid == "quiz":
            is_unlocked = state is not None and state.get("mcqs")
        elif sid == "remediation":
            is_unlocked = state is not None and st.session_state.missed_indices
        elif sid == "complete":
            is_unlocked = st.session_state.step == "complete"

        # Apply different styles for current/unlocked/locked
        btn_label = f"👉 {label}" if is_current else (f"✅ {label}" if is_unlocked else f"⚪ {label}")
        
        if st.button(btn_label, key=f"nav_{sid}", disabled=not is_unlocked, use_container_width=True):
            st.session_state.step = sid
            # If jumping to input, we handle it as a reset-lite or just go back
            st.rerun()

    st.divider()
    
    # 3. Live Metrics
    if state:
        st.markdown(f"### 📊 Live Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Questions", len(state.get("mcqs", [])))
        with col2:
            st.metric("Quality", f"{state.get('relevance_score', 0):.0f}%")
        
        acc = (st.session_state.score / len(state['mcqs']) * 100) if state.get('mcqs') else 0
        st.metric("Current Accuracy", f"{acc:.1f}%")
        
        st.divider()
        if st.button("🔄 Reset Journey", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with st.expander("💡 Learning Tips"):
        st.markdown("""
        - **Navigation**: Click any unlocked step above to revisit material.
        - **Mastery**: Use Review mode to turn mistakes into knowledge!
        """)

# --- Predefined Checkpoints ---
CHECKPOINTS = {
    "Python": {
        "icon": "🐍",
        "desc": "Master the world's most popular language for Data Science.",
        "objectives": ["Python Data Structures", "Functions and Modules", "Object-Oriented Programming"]
    },
    "AI": {
        "icon": "🤖",
        "desc": "Uncover the foundations of Artificial Intelligence and Search.",
        "objectives": ["AI Foundations", "Search Algorithms", "Logic & Reasoning"]
    },
    "ML": {
        "icon": "🧠",
        "desc": "Build predictive models with Machine Learning techniques.",
        "objectives": ["Supervised Learning", "Linear Regression", "Decision Trees"]
    },
    "DL": {
        "icon": "⚡",
        "desc": "Deep dive into Neural Networks and Computer Vision.",
        "objectives": ["Neural Architectures", "Backpropagation", "CNNs & Vision"]
    }
}

# --- Main UI ---
st.markdown('<h1 class="main-title">🤖 Autonomous Learning Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Your AI-powered bridge to rapid knowledge mastery</p>', unsafe_allow_html=True)

if st.session_state.step == "input":
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 🎯 Select Your Mastery Path")
    
    topics = list(CHECKPOINTS.keys())
    selected_topic = st.selectbox("Choose a topic to begin:", topics, index=0)
    
    data = CHECKPOINTS[selected_topic]
    
    st.info(f"**Focus Areas**: {', '.join(data['objectives'])}")
    
    if st.button(f"🚀 Start {selected_topic} Journey", use_container_width=True):
        st.session_state.step = "learning"
        st.session_state.agent_state = {
            "checkpoint": Checkpoint(
                topic=f"{selected_topic} Mastery",
                objectives=data["objectives"],
                success_criteria=[f"Complete assessment for {selected_topic}"]
            ),
            "gathered_info": [],
            "is_relevant": False,
            "relevance_score": 0.0,
            "iterations": 0,
            "messages": [],
            "questions": [],
            "mcqs": [],
            "summary": "",
            "answers": [],
            "score": 0.0,
            "is_streamlit": True,
            "seen_questions": []
        }
        st.rerun()
    

elif st.session_state.step == "learning":
    with st.status("🧠 Gathering and processing knowledge...", expanded=True) as status:
        # Run the graph until it reaches 'questions' node
        # We simulate the flow through nodes manually for better UI feedback
        state = st.session_state.agent_state
        
        st.write("🔍 Searching the web...")
        # Since we refactored agent.py, we can call nodes directly or use app.invoke
        # Here we use app.invoke but we need to stop before verify
        # Actually, let's just run nodes manually for the best Streamlit control
        from agent import start_checkpoint, gather_context_node, validate_context_node, process_context_node, summarize_node, generate_questions_node
        
        if not state["messages"]:
            state.update(start_checkpoint(state))
        
        if "Context gathered." not in state["messages"]:
            state.update(gather_context_node(state))
            st.write("✅ Context gathered.")
            
        if "Relevance check" not in "".join(state["messages"]):
            state.update(validate_context_node(state))
            if not state["is_relevant"]:
                st.error("Failed to find relevant context. Please refine your topic.")
                st.session_state.step = "input"
                st.rerun()
            st.write(f"✅ Context validated (Score: {state.get('relevance_score', 0):.1f}%).")
            
        if "chunks" not in "".join(state["messages"]):
            state.update(process_context_node(state))
            st.write("📂 Context processed into vectors.")
            
        if not state["summary"]:
            state.update(summarize_node(state))
            st.write("📖 Study material generated.")
            
        if not state["mcqs"]:
            state.update(generate_questions_node(state))
            st.write("📝 Practice quiz prepared.")
            
        st.session_state.agent_state = state
        status.update(label="Learning material ready!", state="complete", expanded=False)
    
    # Display Summary
    st.subheader("📚 Study Material")
    st.markdown(f'<div class="summary-card">{state["summary"]}</div>', unsafe_allow_html=True)
    
    if st.button("✍️ Start Practice Quiz"):
        st.session_state.step = "quiz"
        st.rerun()

elif st.session_state.step == "quiz":
    state = st.session_state.agent_state
    mcqs = state["mcqs"]
    
    st.header("📝 Knowledge Check")
    st.info("Answer all questions below and click the button at the bottom to submit your assessment.")
    
    # Initialize user_answers if not present or of wrong length
    if len(st.session_state.user_answers) != len(mcqs):
        st.session_state.user_answers = [None] * len(mcqs)
    
    for i, mcq in enumerate(mcqs):
        st.subheader(f"Question {i + 1}")
        st.write(f"**{mcq.question}**")
        
        options = [f"{idx+1}) {opt}" for idx, opt in enumerate(mcq.options)]
        # Index of selected option or None
        default_idx = None
        if st.session_state.user_answers[i] is not None:
            default_idx = st.session_state.user_answers[i]
            
        st.session_state.user_answers[i] = st.radio(
            "Select your answer:", 
            range(len(options)), 
            format_func=lambda x: options[x],
            key=f"q_radio_{i}",
            index=default_idx
        )
        st.divider()

    if st.button("🚀 Submit My Final Answers", type="primary", use_container_width=True):
        # Calculate scores and missed indices all at once
        correct_count = 0
        st.session_state.missed_indices = []
        
        for i, mcq in enumerate(mcqs):
            user_choice = st.session_state.user_answers[i]
            if user_choice == mcq.correct_index:
                correct_count += 1
            else:
                st.session_state.missed_indices.append(i)
        
        total_mcqs = len(mcqs)
        final_score_pct = (correct_count / total_mcqs) * 100
        st.session_state.score = correct_count
        st.session_state.agent_state["score"] = final_score_pct
        
        if st.session_state.missed_indices:
            st.session_state.step = "remediation"
        else:
            st.session_state.step = "complete"
        st.rerun()

elif st.session_state.step == "remediation":
    state = st.session_state.agent_state
    mcqs = state["mcqs"]
    missed = st.session_state.missed_indices
    
    st.header("🚀 Mastery Review")
    st.warning(f"You missed {len(missed)} concepts. Let's reinforce them with simplified AI explanations.")
    
    # Initialize feynman_explanations dict if not present
    if "feynman_explanations" not in st.session_state:
        st.session_state.feynman_explanations = {}

    # Progress tracker for generation
    pending_indices = [idx for idx in missed if idx not in st.session_state.feynman_explanations]
    
    if pending_indices:
        with st.status("🧠 Crafting simplified explanations for your review...", expanded=True) as status:
            from context_utils import generate_feynman_explanation
            from search_utils import search_for_simple_explanation
            for idx in pending_indices:
                mcq = mcqs[idx]
                st.write(f"Refining: *{mcq.question}*...")
                simple_context = search_for_simple_explanation(mcq.question)
                explanation = generate_feynman_explanation(mcq.question, state["checkpoint"].context, simple_context)
                st.session_state.feynman_explanations[idx] = explanation
            status.update(label="All explanations ready!", state="complete", expanded=False)
            st.rerun()

    # Display all explanations
    for idx in missed:
        mcq = mcqs[idx]
        with st.expander(f"📌 Concept: {mcq.question}", expanded=True):
            st.markdown(f"""
            <div class="summary-card" style="border-left: 6px solid #4CAF50; background-color: #f9fff9; margin-bottom: 1rem;">
                {st.session_state.feynman_explanations[idx]}
            </div>
            """, unsafe_allow_html=True)
            st.info(f"💡 The correct answer was: **{mcq.options[mcq.correct_index]}**")

    st.divider()
    if st.button("🔄 Retake Practice Quiz", type="primary", use_container_width=True):
        # LOOP BACK: Reset quiz state for a fresh round
        st.session_state.step = "learning"
        st.session_state.score = 0
        st.session_state.quiz_index = 0
        st.session_state.missed_indices = []
        st.session_state.remediation_index = 0
        st.session_state.user_answers = []
        if "feynman_explanations" in st.session_state:
            del st.session_state.feynman_explanations
        # Clear mcqs to trigger regeneration
        st.session_state.agent_state["mcqs"] = []
        st.rerun()

elif st.session_state.step == "complete":
    state = st.session_state.agent_state
    total = len(state["mcqs"])
    final_score = (st.session_state.score / total) * 100
    
    st.balloons()
    st.image("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80", caption="Level up your skills with AI-guided learning.")
    st.success(f"🎊 Journey Complete! Your final score: **{final_score:.1f}%**")
    
    st.subheader("📊 Performance Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Correct", f"{st.session_state.score} / {total}")
    col2.metric("Accuracy", f"{final_score:.1f}%")
    col3.metric("Context Quality", f"{state.get('relevance_score', 0):.1f}%")
    
    if final_score >= 70:
        st.info("🎯 **Mastery Achieved!** You have met the 70% proficiency threshold.")
    else:
        st.warning("💪 **Keep Practicing.** Although you finished remediation, your initial score was below 70%.")
    
    if st.button("🎯 Start a New Topic"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
