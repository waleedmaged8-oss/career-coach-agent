import logging
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from core.config import TARGET_ROLES

logger = logging.getLogger("CareerCoach.SkillGapAgent")

SKILL_GAP_SYSTEM_INSTRUCTION = """
You are an expert AI Career Coach specializing in Skill Gap Analysis for technical roles: Data Analyst, Data Scientist, AI Engineer, and Machine Learning Engineer.
Your objective is to analyze a candidate's current professional background, skills, and projects, and compare them against the industry requirements for their target role.

For the analysis:
1. Provide an estimated "Match Score" (percentage) indicating how close they are to the target role.
2. Outline the "Overlapping Skills" they already possess.
3. Classify the "Skill Gaps" into three categories:
   - Critical/Foundational Gaps (Must-have to land any job in this role)
   - Specialized Gaps (Important for mid-to-senior levels or specific domains)
   - Tools & Framework Gaps (Specific libraries, platforms, or tools)
4. Offer strategic advice on what to prioritize first.

Ensure your output is structured in clean, professional Markdown. Use clear headings, bullet points, and highlight key terms using bold text.
"""

class SkillGapAgent(BaseAgent):
    """
    SkillGapAgent performs a detailed gap analysis between the user's current skillset
    and the target career path.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(
            name="SkillGapAgent",
            system_instruction=SKILL_GAP_SYSTEM_INSTRUCTION,
            model_name=model_name
        )

    def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Runs the skill gap analysis.
        Expects context to contain:
        - target_role: The role the user is targeting.
        - current_skills: The user's self-reported current skills.
        - current_experience: The user's work/academic background.
        """
        context = context or {}
        target_role = context.get("target_role", "Data Scientist")
        current_skills = context.get("current_skills", "Not provided")
        current_experience = context.get("current_experience", "Not provided")
        
        role_description = TARGET_ROLES.get(target_role, "")
        
        prompt = f"""
Target Role: {target_role}
Role Overview: {role_description}

Candidate Profile:
- Current Experience/Background: {current_experience}
- Self-Reported Current Skills: {current_skills}
- Additional Context/User Input: {user_input}

Please perform a detailed Skill Gap Analysis and output your assessment.
"""
        return self.call_llm(prompt, temperature=0.5)
