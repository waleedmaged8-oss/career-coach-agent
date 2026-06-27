import logging
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from core.config import TARGET_ROLES

logger = logging.getLogger("CareerCoach.InterviewAgent")

INTERVIEW_SYSTEM_INSTRUCTION = """
You are an expert technical interviewer specializing in hiring Data Analysts, Data Scientists, AI Engineers, and Machine Learning Engineers.
Your goal is to prepare candidates for real-world technical and behavioral interviews.

You operate in two modes depending on the instructions in the prompt:
1. **Question Generation Mode**: Generate a challenging, realistic interview question appropriate for the target role and experience level. The question can be theoretical, coding/SQL-based, system design, or behavioral.
2. **Evaluation Mode**: Analyze the candidate's response to a specific question. Provide:
   - A score (e.g., Poor, Fair, Good, Excellent).
   - Constructive critique (what they did well, what was missing).
   - The ideal model answer or key concepts that should have been mentioned.
   - Actionable tips to improve delivery or structure (e.g., using the STAR method for behavioral questions).

Keep your tone professional, constructive, and realistic. Output in clean Markdown format.
"""

class InterviewAgent(BaseAgent):
    """
    InterviewAgent generates mock interview questions and provides constructive feedback
    on user answers.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(
            name="InterviewAgent",
            system_instruction=INTERVIEW_SYSTEM_INSTRUCTION,
            model_name=model_name
        )

    def generate_question(self, target_role: str, focus_area: Optional[str] = None, experience_level: str = "Junior/Mid") -> str:
        """
        Generates an interview question for the target role.
        """
        role_description = TARGET_ROLES.get(target_role, "")
        focus_prompt = f" focusing on the area of '{focus_area}'" if focus_area else ""
        
        prompt = f"""
[GENERATE_QUESTION]
Target Role: {target_role}
Role Overview: {role_description}
Candidate Experience Level: {experience_level}
{focus_prompt}

Please generate ONE realistic interview question. Do not output the answer, just the question. Provide a brief setup if it's a scenario-based or system design question.
"""
        return self.call_llm(prompt, temperature=0.7)

    def evaluate_answer(self, target_role: str, question: str, user_answer: str) -> str:
        """
        Evaluates the user's answer to a specific interview question.
        """
        prompt = f"""
[EVALUATE]
Target Role: {target_role}
Question Asked: {question}
Candidate's Answer: {user_answer}

Please evaluate the answer. Provide a constructive review, highlight what was good, what was missing, outline the ideal solution/concepts, and suggest improvements.
"""
        return self.call_llm(prompt, temperature=0.5)

    def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Fallback run method. Directs to generation or evaluation based on context.
        """
        context = context or {}
        mode = context.get("mode", "generate")
        target_role = context.get("target_role", "Data Scientist")
        
        if mode == "evaluate":
            question = context.get("current_question", "State your background.")
            return self.evaluate_answer(target_role, question, user_input)
        else:
            focus_area = context.get("focus_area")
            experience_level = context.get("experience_level", "Junior/Mid")
            return self.generate_question(target_role, focus_area, experience_level)
