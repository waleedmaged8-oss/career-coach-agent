import json
import os

SESSION_FILE = "session.json"


def save_session(session):
    data = {
        "target_role": session.target_role,
        "current_skills": session.current_skills,
        "current_experience": session.current_experience,
        "skill_gaps": session.skill_gaps,
    }

    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_session(session):
    if not os.path.exists(SESSION_FILE):
        return session

    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    session.target_role = data.get("target_role")
    session.current_skills = data.get("current_skills")
    session.current_experience = data.get("current_experience")
    session.skill_gaps = data.get("skill_gaps")

    return session