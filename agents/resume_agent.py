import logging
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from core.config import TARGET_ROLES

logger = logging.getLogger("CareerCoach.ResumeAgent")

RESUME_SYSTEM_INSTRUCTION = """
You are an expert Executive Resume Reviewer and Technical Recruiter.
Your objective is to review a candidate's resume text and provide highly actionable feedback to align it with their target role (Data Analyst, Data Scientist, AI Engineer, or Machine Learning Engineer).

For the review:
1. Provide an overall summary of the resume's strengths and weaknesses.
2. Analyze "Keyword Alignment": Identify missing technical keywords and industry-standard tools for the target role that are absent or under-represented.
3. Suggest "Bullet Point Enhancements": Take 2-3 weak or standard lines from the resume and rewrite them using the STAR/XYZ formula: "Accomplished [X], as measured by [Y], by doing [Z]."
4. Evaluate "Format & Structure": Give tips on section hierarchy, readability, and how to structure project descriptions.

Ensure the feedback is constructive, specific, and direct. Output in clean Markdown format.
"""

class ResumeAgent(BaseAgent):
    """
    ResumeAgent analyzes resume text and suggests optimization tips for ATS and hiring managers.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(
            name="ResumeAgent",
            system_instruction=RESUME_SYSTEM_INSTRUCTION,
            model_name=model_name
        )

    def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Runs the resume review.
        Expects context to contain:
        - target_role: The role the user is targeting.
        
        The `user_input` is expected to be the raw text of the user's resume.
        """
        context = context or {}
        target_role = context.get("target_role", "Data Scientist")
        role_description = TARGET_ROLES.get(target_role, "")
        
        prompt = f"""
Target Role: {target_role}
Role Overview: {role_description}

Candidate's Resume Content:
---
{user_input}
---

Please perform a detailed resume review and provide specific optimization feedback.
"""
        return self.call_llm(prompt, temperature=0.5)
