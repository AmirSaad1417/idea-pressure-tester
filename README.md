# ⚡ Idea Pressure Tester

> **Stress-test and pressure-test your startup ideas with an AI panel of 4 distinct personas and real-time market discovery.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by Gemini](https://img.shields.io/badge/AI-Google%20Gemini%20%7C%20OpenAI-orange)](https://aistudio.google.com/)

---

## 📌 Overview

**Idea Pressure Tester** is an AI-powered evaluation tool designed for founders, indie hackers, and product managers. Instead of relying on generic feedback, the app evaluates your pitch through **four specialized personas** with contrasting perspectives, paired with an automated **competitor landscape discovery** engine.

### 👥 The 4 Expert Personas
- **📈 Investor (Green / Success):** Evaluates total addressable market (TAM), unit economics, return on capital, and scalability.
- **🛡️ Skeptic (Red / Error):** Uncovers fatal flaws, user acquisition bottlenecks, regulatory hurdles, and churn risks.
- **🎯 Customer (Blue / Info):** Analyzes everyday utility, willingness to pay, and friction points.
- **⚔️ Competitor (Yellow / Warning):** Evaluates defensibility, moat, and how incumbents will respond.

---

## 🏗️ Project Architecture

```
idea-pressure-tester/
├── src/
│   ├── app.py            # Interactive Streamlit Web UI & Teach Mode
│   └── main.py           # Core AI evaluation engine & Standalone CLI
├── .env.example          # Environment variable template
├── .gitignore            # Protects credentials and local caches
├── LICENSE               # MIT License
├── requirements.txt      # Production dependencies
└── README.md             # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/AmirSaad1417/idea-pressure-tester.git
cd idea-pressure-tester
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and configure your API key:
```env
# Free Google Gemini API Key (get from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: OpenAI API Key (from https://platform.openai.com/)
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 💻 Usage

### 🖥️ 1. Interactive Streamlit Web UI
Run the Streamlit application:
```bash
streamlit run src/app.py
```
Open your browser at `http://localhost:8501`.

#### Features:
- **Instant Idea Pre-filling**: Click one of the three example idea pill buttons to populate the text area.
- **Concurrent Analysis**: Personas and market discovery execute in parallel for fast responses.
- **🎓 Teach Mode ("Show me how it works")**: Toggle the checkbox to inspect:
  - **Role Prompting**: View the exact system prompt.
  - **Structured Output**: Inspect raw JSON schemas.
  - **Tool Usage**: View the market query and model payload.
- **Safe Reset**: "Try another idea" resets the session state without losing context.

### ⌨️ 2. Standalone CLI Script
Run the engine directly in the terminal:
```bash
python src/main.py
```

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Fork or push this repository to your GitHub account (`AmirSaad1417/idea-pressure-tester`).
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **"New app"** and select:
   - **Repository:** `AmirSaad1417/idea-pressure-tester`
   - **Branch:** `main`
   - **Main file path:** `src/app.py`
4. In **Advanced Settings > Secrets**, paste your key:
   ```toml
   GEMINI_API_KEY = "your_actual_key_here"
   ```
5. Click **Deploy!**

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

Developed with ❤️ by [Amir Saad](https://github.com/AmirSaad1417).
