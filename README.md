# 🚀 Rosetta Agent

Rosetta Agent is an autonomous, self-healing framework designed to intercept failed CI/CD pipelines, diagnose runtime errors, and automatically deploy targeted code patches. Powered by the Google GenAI SDK and Streamlit, Rosetta bridges the gap between terminal crash logs and instant repository remediation.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://rosetta-agent-d7ajwox4fnkhrzd5txnw9e.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/DarthPandey/Rosetta-Agent/blob/main/LICENSE)

---

## 💡 The Core Problem
Digging through thousands of lines of raw terminal logs to find a single syntax error, broken environment variable, or dependency mismatch wastes critical engineering hours. Rosetta turns a red, broken pipeline into a passing green build autonomously.

## ✨ Key Features
* **Pipeline Interception:** Hooks directly into the GitLab REST API to monitor remote development environments and programmatically grab raw console logs from failing pipelines.
* **AI Cognition Layer (`gemini-2.5-flash`):** Utilizes the Google GenAI SDK to isolate stack traces, diagnose root causes, and generate raw, precise, executable code patches.
* **Automated Hot-Patching:** Formats and executes automated Git commits directly back into the remote repository to fix the bug instantly.
* **Streamlit Command Center:** A clean, intuitive dashboard to monitor agent cognition, review proposed code patches, and track automated deployment statuses in real-time.

---

## 🛠️ Tech Stack
* **LLM Engine:** Google Gemini API (`gemini-2.5-flash`) via the `google-genai` Python SDK
* **Frontend/Hosting:** Streamlit & Streamlit Community Cloud
* **DevOps Integration:** GitLab REST API
* **Version Control:** Git & GitHub

---

## ⚙️ Local Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/DarthPandey/Rosetta-Agent.git](https://github.com/DarthPandey/Rosetta-Agent.git)
cd Rosetta-Agent
```

### 2. Install Dependencies
Make sure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a local `.env` file or export your security tokens directly into your terminal environment:
```env
GITLAB_TOKEN="your_gitlab_personal_access_token_here"
GEMINI_API_KEY="your_google_gemini_api_key_here"
```

### 4. Run the Interface
Launch the Streamlit web dashboard locally:
```bash
streamlit run ui.py
```

---

## 📜 License
This project is open-source software licensed under the **MIT License**. See the `LICENSE` file for full details.
