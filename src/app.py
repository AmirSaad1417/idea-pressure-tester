import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to sys.path so "from main import ..." works seamlessly
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import main
import importlib
importlib.reload(main)
from main import get_persona_reactions, get_web_search_summary

st.set_page_config(page_title="Idea Pressure Tester", page_icon="⚡", layout="wide")

# Load environment variables
load_dotenv()

st.title("⚡ Idea Pressure Tester")
st.caption("Pitch your startup idea. An AI board of four distinct expert personas will pressure-test it from every angle.")

# Handle reset request before text_area widget is instantiated
if st.session_state.get("reset_requested"):
    st.session_state["idea_input"] = ""
    st.session_state["reactions"] = None
    st.session_state["web_summary"] = None
    st.session_state["system_prompt"] = ""
    st.session_state["raw_json_response"] = ""
    st.session_state["search_request"] = {}
    st.session_state["reset_requested"] = False

# Sidebar: Founder-centric guidance instead of technical jargon
with st.sidebar:
    st.header("🎯 Meet the Evaluation Panel")
    st.markdown(
        """
        Instead of generic advice, your idea is rigorously judged by four distinct viewpoints:

        - 📈 **Investor**: Evaluates total addressable market (TAM), unit economics, monetization, and exit potential.
        - 🛡️ **Skeptic**: Uncovers fatal flaws, user acquisition bottlenecks, regulatory risks, and churn traps.
        - 🎯 **Customer**: Judges everyday utility, friction points, and real willingness to pay.
        - ⚔️ **Competitor**: Assesses defensibility, moats, and how existing market leaders will respond.
        """
    )

    st.markdown("---")
    st.subheader("💡 Pitching Tips")
    st.markdown(
        """
        For the sharpest, most constructive critiques:
        1. **Specify your target user** (e.g., college students, solo founders, dentists).
        2. **Explain the urgent pain point** they face today.
        3. **Describe your solution** and how you plan to charge.
        """
    )

    # Optional configuration: only shown if no key is found or inside a quiet expander
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))

    if not has_gemini and not has_openai:
        st.markdown("---")
        st.warning("⚠️ No backend API key detected.")
        user_key = st.text_input("Enter Gemini or OpenAI API Key:", type="password")
        if user_key.strip():
            os.environ["GEMINI_API_KEY"] = user_key.strip()
            st.rerun()
    else:
        with st.expander("⚙️ Advanced Settings (Optional)"):
            st.caption("Backend is active and ready.")
            custom_key = st.text_input("Use your own API key:", type="password")
            if custom_key.strip():
                os.environ["GEMINI_API_KEY"] = custom_key.strip()
                st.success("Custom key applied!")

# Initialize session state variables
if "idea_input" not in st.session_state:
    st.session_state["idea_input"] = ""
if "reactions" not in st.session_state:
    st.session_state["reactions"] = None
if "web_summary" not in st.session_state:
    st.session_state["web_summary"] = None
if "system_prompt" not in st.session_state:
    st.session_state["system_prompt"] = ""
if "raw_json_response" not in st.session_state:
    st.session_state["raw_json_response"] = ""
if "search_request" not in st.session_state:
    st.session_state["search_request"] = {}


def set_example_idea(text: str):
    st.session_state["idea_input"] = text


# Text area for user idea input
st.text_area(
    "Pitch your idea:",
    key="idea_input",
    height=130,
    placeholder="Example: An app that connects solo founders with accountability partners and tracks weekly milestone commitments...",
)

# Clickable pill buttons for quick example ideas
st.markdown("**Or explore an example:**")
col1, col2, col3 = st.columns(3)
with col1:
    st.button(
        "📚 Study partners nearby",
        key="pill_1",
        on_click=set_example_idea,
        args=("An app that finds study partners nearby",),
        use_container_width=True,
    )
with col2:
    st.button(
        "🍜 Street food subscription",
        key="pill_2",
        on_click=set_example_idea,
        args=("A subscription box for local street food",),
        use_container_width=True,
    )
with col3:
    st.button(
        "📑 Auto assignment citations",
        key="pill_3",
        on_click=set_example_idea,
        args=("AI that writes university assignment citations automatically",),
        use_container_width=True,
    )

st.write("")
pressure_test_clicked = st.button("🚀 Pressure Test It", type="primary")

if pressure_test_clicked:
    current_idea = st.session_state.get("idea_input", "").strip()
    if not current_idea:
        st.warning("Please enter your startup idea or click one of the examples above first.")
    else:
        # 1. Persona reactions call
        try:
            with st.spinner("Convening the evaluation panel (Investor, Skeptic, Customer, Competitor)..."):
                reactions = get_persona_reactions(current_idea)
                st.session_state["reactions"] = reactions
                st.session_state["system_prompt"] = main.SYSTEM_PROMPT
                st.session_state["raw_json_response"] = main.last_raw_json
        except Exception as e:
            st.error(f"Error during persona analysis: {e}")
            st.session_state["reactions"] = None

        # 2. Market landscape discovery call
        if st.session_state.get("reactions"):
            try:
                with st.spinner("Scanning the competitive landscape for similar existing products..."):
                    summary = get_web_search_summary(current_idea)
                    st.session_state["web_summary"] = summary
                    st.session_state["search_request"] = main.last_search_request
            except Exception as e:
                st.error(f"Error during market discovery: {e}")
                st.session_state["web_summary"] = "No closely similar products found."

# Display persona responses and web search summary
if st.session_state.get("reactions"):
    reactions = st.session_state["reactions"]

    st.write("---")
    st.subheader("📊 Panel Verdict")

    # 2x2 grid using st.columns
    # Row 1: Customer (info) & Investor (success)
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.subheader("🎯 Customer Reaction")
        st.info(reactions.get("customer", ""))

    with row1_col2:
        st.subheader("📈 Investor Verdict")
        st.success(reactions.get("investor", ""))

    # Row 2: Competitor (warning) & Skeptic (error)
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.subheader("⚔️ Competitor Response")
        st.warning(reactions.get("competitor", ""))

    with row2_col2:
        st.subheader("🛡️ Skeptic's Warning")
        st.error(reactions.get("skeptic", ""))

    # Market landscape summary
    if st.session_state.get("web_summary"):
        st.write("---")
        st.subheader("🌐 Existing Market Landscape & Competitors")
        st.write(st.session_state["web_summary"])

    # Collapsible behind-the-scenes inspection for curious users & developers
    with st.expander("🔍 Behind the Scenes (Prompt & Schema Inspector)"):
        st.markdown("**Role Prompting Sent to AI:**")
        st.code(st.session_state.get("system_prompt", ""))
        st.markdown("**Structured JSON Output:**")
        st.code(st.session_state.get("raw_json_response", ""), language="json")
        st.markdown("**Market Discovery Query:**")
        st.code(json.dumps(st.session_state.get("search_request", {}), indent=2), language="json")

    st.write("")
    if st.button("🔄 Try another idea"):
        st.session_state["reset_requested"] = True
        st.session_state["reactions"] = None
        st.session_state["web_summary"] = None
        st.rerun()
