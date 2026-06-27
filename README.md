# AI Career Coach Agent

A production-ready, multi-agent AI Career Coach in Python. The system helps candidates plan their transition or advancement toward four high-demand technical roles: **Data Analyst**, **Data Scientist**, **AI Engineer**, and **Machine Learning Engineer**.

Using a modular multi-agent architecture and built-in security guardrails, the career coach guides users through profile building, skill gap analysis, customized learning roadmaps, resume feedback, and stateful mock interviews.

---

## Architecture Overview

The application features a central orchestrator that coordinates specialized agents using the official Google GenAI SDK:

```
                  ┌────────────────────────┐
                  │       User CLI         │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │      Orchestrator      │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │     Security Agent     │
                  └─────┬────────────┬─────┘
                        │            │
            (If Safe)   │            │ (If Unsafe)
      ┌─────────────────┘            └─────────────────┐
      ▼                                                ▼
┌──────────────┬──────────────┬──────────────┬───┐   ┌──────────────────┐
│  Skill Gap   │   Roadmap    │  Interview   │...│   │  Block & Warn    │
│  Analysis    │  Generator   │ Preparation  │   │   │  Candidate       │
└──────────────┴──────────────┴──────────────┴───┘   └──────────────────┘
```

### Specialized Agents:
1. **Security Agent**: Enforces data safety and guards against adversarial prompts.
   - **PII Redactor**: Employs fast, local Regex rules to strip emails and phone numbers *before* sending to the cloud, combined with LLM-assisted redaction to catch names and sensitive locations.
   - **Prompt Injection Detector**: Evaluates prompts to identify overrides, system bypass attempts, or jailbreaks, returning a structured safety verdict.
2. **Skill Gap Analysis Agent**: Evaluates user profiles against target role standards to provide a match score, highlights overlapping skills, and isolates critical technical, tool, and soft skill gaps.
3. **Learning Roadmap Agent**: Creates customized learning phases featuring core concepts, practical milestone projects, and curated learning references.
4. **Interview Preparation Agent**: Conducts dynamic, stateful mock interviews. It outputs challenging questions and evaluates candidates' responses with constructive critiques and ideal solutions.
5. **Resume Review Agent**: Assesses resume text to offer keyword optimization, format feedback, and STAR-formula rewrites.

---

## File Structure

```
career-coach-agent/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Abstract base agent class
│   ├── security_agent.py      # Regex + LLM-based security guardrails
│   ├── skill_gap_agent.py     # Skill alignment & gap analysis
│   ├── roadmap_agent.py       # Personalized study roadmap generator
│   ├── interview_agent.py     # Technical question generator and evaluator
│   └── resume_agent.py        # ATS-optimized resume feedback
│
├── core/
│   ├── __init__.py
│   ├── config.py              # Environment configuration & GenAI Client
│   └── orchestrator.py        # Sessions manager and routing orchestrator
│
├── ui/
│   ├── __init__.py
│   └── cli.py                 # ANSI-colored console interface
│
├── tests/
│   ├── __init__.py
│   └── test_agents.py         # Unit test suite
│
├── README.md
├── requirements.txt
└── main.py                    # App entrypoint
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- A Google Gemini API Key

### Installation

1. Clone or copy the project files to your workspace directory.
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration
Create a `.env` file in the root directory and add your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(Alternatively, you can export `GEMINI_API_KEY` directly to your environment variables.)*

---

## Running the Application

Launch the interactive CLI dashboard:
```bash
python main.py
```

### Navigating the App:
1. **Target Goal Selection**: On startup, choose your target role (e.g., AI Engineer).
2. **Set/Update Profile**: Input your educational background and current skills.
3. **Skill Gap Analysis**: Find out what you are missing.
4. **Custom Roadmap**: Generate a step-by-step roadmap to study and build projects.
5. **Stateful Mock Interview**: Practice in a 3-round interactive interview. Submit your answers and get immediate feedback.
6. **Resume Review**: Paste your resume text to optimize it for recruiters.

---

## Running the Tests

Unit tests are written using python's built-in `unittest` library and mock external API calls to run fully offline without consuming API tokens:

```bash
python -m unittest discover -s tests
```
