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

st.set_page_config(page_title="Idea Pressure Tester", page_icon="💡", layout="wide")

# Load environment variables
load_dotenv()

st.title("Idea Pressure Tester")
st.caption("Pitch your idea. Four personas will judge it.")

# 1. Teach mode checkbox at the top
show_teach_mode = st.checkbox("Show me how it works")

# Handle reset request before text_area widget is instantiated
if st.session_state.get("reset_requested"):
    st.session_state["idea_input"] = ""
    st.session_state["reactions"] = None
    st.session_state["web_summary"] = None
    st.session_state["system_prompt"] = ""
    st.session_state["raw_json_response"] = ""
    st.session_state["search_request"] = {}
    st.session_state["reset_requested"] = False

# Sidebar for API key status and optional input
with st.sidebar:
    st.header("⚙️ API Configuration")
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))

    if not has_gemini and not has_openai:
        st.warning("⚠️ No API key found in `.env`")
        st.markdown(
            "Get a **100% free key** (no credit card needed) at:  \n"
            "[👉 Google AI Studio](https://aistudio.google.com/)"
        )
        user_key = st.text_input("Paste Gemini API Key here:", type="password")
        if user_key.strip():
            os.environ["GEMINI_API_KEY"] = user_key.strip()
            try:
                env_path = Path(__file__).resolve().parent.parent / ".env"
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(f"GEMINI_API_KEY={user_key.strip()}\n")
            except Exception:
                pass
            st.success("API Key saved! Ready to test.")
            st.rerun()
    else:
        if os.getenv("OPENAI_API_KEY"):
            st.success("Active Provider: OpenAI")
        else:
            st.success("Active Provider: Google Gemini (Free)")

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
    height=120,
    placeholder="Describe your startup or product idea here...",
)

# Small clickable pill buttons below the textarea as example ideas
col1, col2, col3 = st.columns(3)
with col1:
    st.button(
        "An app that finds study partners nearby",
        key="pill_1",
        on_click=set_example_idea,
        args=("An app that finds study partners nearby",),
        use_container_width=True,
    )
with col2:
    st.button(
        "A subscription box for local street food",
        key="pill_2",
        on_click=set_example_idea,
        args=("A subscription box for local street food",),
        use_container_width=True,
    )
with col3:
    st.button(
        "AI that writes university assignment citations automatically",
        key="pill_3",
        on_click=set_example_idea,
        args=("AI that writes university assignment citations automatically",),
        use_container_width=True,
    )

st.write("")
pressure_test_clicked = st.button("Pressure Test It", type="primary")

if pressure_test_clicked:
    current_idea = st.session_state.get("idea_input", "").strip()
    if not current_idea:
        st.warning("Please enter an idea or select an example above first.")
    else:
        # 1. Persona reactions call
        try:
            with st.spinner("Analyzing your idea..."):
                reactions = get_persona_reactions(current_idea)
                st.session_state["reactions"] = reactions
                # 2. Capture and store telemetry for teach mode
                st.session_state["system_prompt"] = main.SYSTEM_PROMPT
                st.session_state["raw_json_response"] = main.last_raw_json
        except Exception as e:
            st.error(f"Error during persona analysis: {e}")
            st.session_state["reactions"] = None

        # 2. Web search summary call
        if st.session_state.get("reactions"):
            try:
                with st.spinner("Searching the web..."):
                    summary = get_web_search_summary(current_idea)
                    st.session_state["web_summary"] = summary
                    # 2. Capture search request for teach mode
                    st.session_state["search_request"] = main.last_search_request
            except Exception as e:
                st.error(f"Error during web search: {e}")
                st.session_state["web_summary"] = "No closely similar products found."

# Display persona responses and web search summary
if st.session_state.get("reactions"):
    reactions = st.session_state["reactions"]

    st.write("---")
    # 2x2 grid using st.columns
    # Row 1: Customer (info) & Investor (success)
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.subheader("Customer")
        st.info(reactions.get("customer", ""))

    with row1_col2:
        st.subheader("Investor")
        st.success(reactions.get("investor", ""))

    # Row 2: Competitor (warning) & Skeptic (error)
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.subheader("Competitor")
        st.warning(reactions.get("competitor", ""))

    with row2_col2:
        st.subheader("Skeptic")
        st.error(reactions.get("skeptic", ""))

    # Web search summary
    if st.session_state.get("web_summary"):
        st.write("---")
        st.subheader("Similar ideas on the web")
        st.write(st.session_state["web_summary"])

    # 3. Teach mode display if show_teach_mode is True
    if show_teach_mode:
        st.write("---")
        with st.expander("Role prompting"):
            st.code(st.session_state.get("system_prompt", ""))

        with st.expander("Structured output"):
            st.code(st.session_state.get("raw_json_response", ""), language="json")

        with st.expander("Tool usage"):
            st.code(json.dumps(st.session_state.get("search_request", {}), indent=2), language="json")

    st.write("")
    if st.button("Try another idea"):
        st.session_state["reset_requested"] = True
        st.session_state["reactions"] = None
        st.session_state["web_summary"] = None
        st.rerun()
