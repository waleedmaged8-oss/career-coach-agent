import logging
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from core.config import TARGET_ROLES

logger = logging.getLogger("CareerCoach.RoadmapAgent")

ROADMAP_SYSTEM_INSTRUCTION = """
You are an expert AI Career Roadmap Planner. Your job is to design highly customized, actionable learning pathways for aspiring Data Analysts, Data Scientists, AI Engineers, and Machine Learning Engineers.
Your roadmaps must translate conceptual gaps into structural learning milestones.

For each milestone in the roadmap, you must include:
1. Milestone Title & Estimated Timeline (based on user's availability if provided, otherwise assume standard pacing).
2. Key Topics: Core theoretical concepts to master.
3. Recommended Practical Projects: Concrete hands-on projects they should build to prove competence. Describe project ideas clearly.
4. Suggested Resources: Official documentation links, high-quality open-source tutorials, and general courses.

Make the roadmap clear, encouraging, structured, and easy to follow. Output in clean Markdown format with bold highlights.
"""

class RoadmapAgent(BaseAgent):
    """
    RoadmapAgent creates a chronological, project-based learning plan designed to bridge
    the user's skill gaps.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(
            name="RoadmapAgent",
            system_instruction=ROADMAP_SYSTEM_INSTRUCTION,
            model_name=model_name
        )

    def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Runs the learning roadmap generator.
        Expects context to contain:
        - target_role: The role the user is targeting.
        - skill_gaps: The analyzed skill gaps (ideally output from the SkillGapAgent).
        - timeline_pref: Optional user preference for timeline or weekly hours (e.g., "3 months, 10 hours/week").
        """
        context = context or {}
        target_role = context.get("target_role", "Data Scientist")
        skill_gaps = context.get("skill_gaps", "Not specified yet")
        timeline_pref = context.get("timeline_pref", "Flexible / standard pacing")
        
        role_description = TARGET_ROLES.get(target_role, "")
        
        prompt = f"""
Target Role: {target_role}
Role Overview: {role_description}
Time Commitment / Timeline Preference: {timeline_pref}

Identified Skill Gaps to Bridge:
{skill_gaps}

Additional User Preferences / Context: {user_input}

Please design a structured, milestone-based learning roadmap to bridge these gaps and prepare the user for job applications.
"""
        return self.call_llm(prompt, temperature=0.6)
