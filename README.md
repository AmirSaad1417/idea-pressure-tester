# idea-pressure-tester

A Python project for stress-testing and pressure-testing startup and product ideas.

## Project Structure

```
idea-pressure-tester/
├── src/
│   ├── app.py
│   └── main.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone or open the repository** and navigate to the project directory:
   ```bash
   cd idea-pressure-tester
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Copy `.env.example` to `.env` and set your OpenAI API key:
   ```bash
   # Windows (PowerShell)
   Copy-Item .env.example .env

   # macOS / Linux
   cp .env.example .env
   ```

   Then open `.env` and replace `your-key-here` with your actual OpenAI API key:
   ```env
   OPENAI_API_KEY=your-actual-api-key
   ```

## Usage

### 1. Launch the Streamlit Web UI
```bash
streamlit run src/app.py
```

### 2. Run CLI / Standalone Script
```bash
python src/main.py
```
