import logging
from typing import Dict, Any, Optional, Tuple, List
from agents.security_agent import SecurityAgent
from agents.skill_gap_agent import SkillGapAgent
from agents.roadmap_agent import RoadmapAgent
from agents.interview_agent import InterviewAgent
from agents.resume_agent import ResumeAgent
from core.session_manager import save_session, load_session

logger = logging.getLogger("CareerCoach.Orchestrator")

class UserSession:
    """
    Holds the state of a single user interaction session.
    """
    def __init__(self):
        self.target_role: Optional[str] = None
        self.current_skills: Optional[str] = None
        self.current_experience: Optional[str] = None
        self.skill_gaps: Optional[str] = None
        
        # Interview State
        self.interview_active: bool = False
        self.interview_experience: str = "Junior/Mid"
        self.interview_focus: Optional[str] = None
        self.interview_questions: List[str] = []
        self.interview_answers: List[str] = []
        self.interview_evaluations: List[str] = []
        self.current_question: Optional[str] = None

class Orchestrator:
    """
    Orchestrator acts as the central controller of the career coach.
    It intercepts all inputs with the SecurityAgent, maintains UserSession state,
    and routes user requests to the appropriate specialized agents.
    """
    
    def __init__(self):
        # Initialize all agents
        self.security_agent = SecurityAgent()
        self.skill_gap_agent = SkillGapAgent()
        self.roadmap_agent = RoadmapAgent()
        self.interview_agent = InterviewAgent()
        self.resume_agent = ResumeAgent()
        
        # Session state
        self.session = load_session(UserSession())

    def process_input(self, user_input: str) -> Tuple[bool, str, str]:
        """
        Processes user input by first running it through the SecurityAgent.
        Returns:
            Tuple[bool, str, str]: (is_safe, cleaned_text, error_or_info_message)
        """
        security_res = self.security_agent.run(user_input)
        if not security_res.get("is_safe", False):
            # Guardrails triggered
            logger.warning("Guardrails blocked input.")
            return False, user_input, security_res.get("reason", "Security check failed.")
            
        return True, security_res.get("cleaned_text", user_input), ""

    def set_target_role(self, role: str) -> None:
        self.session.target_role = role
        save_session(self.session)

    def update_profile(self, experience: str, skills: str) -> None:
        """Updates user background and self-reported skills."""
        self.session.current_experience = experience
        self.session.current_skills = skills
        save_session(self.session)

    def run_skill_gap_analysis(self, additional_info: str = "") -> str:
        """
        Validates target role, runs security check, and performs skill gap analysis.
        """
        if not self.session.target_role:
            return "Please select a target role first."
            
        # Run security check
        is_safe, cleaned_info, error_msg = self.process_input(additional_info)
        if not is_safe:
            return error_msg
            
        context = {
            "target_role": self.session.target_role,
            "current_skills": self.session.current_skills or "Not provided",
            "current_experience": self.session.current_experience or "Not provided"
        }
        
        logger.info(f"Running Skill Gap Analysis for role: {self.session.target_role}")
        analysis = self.skill_gap_agent.run(cleaned_info, context=context)
        
        # Save result to session state to help the roadmap agent build on it
        self.session.skill_gaps = analysis
        save_session(self.session)
        return analysis

    def run_learning_roadmap(self, additional_info: str = "", timeline: str = "Flexible") -> str:
        """
        Generates a milestone-based learning roadmap using the gaps identified.
        """
        if not self.session.target_role:
            return "Please select a target role first."
            
        is_safe, cleaned_info, error_msg = self.process_input(additional_info)
        if not is_safe:
            return error_msg
            
        # If gap analysis hasn't been run yet, trigger a simplified one or notify
        gaps = self.session.skill_gaps or "Not analyzed yet. Assume typical skills needed for this role."
        
        context = {
            "target_role": self.session.target_role,
            "skill_gaps": gaps,
            "timeline_pref": timeline
        }
        
        logger.info(f"Generating Roadmap for role: {self.session.target_role}")
        roadmap = self.roadmap_agent.run(cleaned_info, context=context)
        return roadmap

    def start_interview_session(self, focus_area: Optional[str] = None, experience_level: str = "Junior/Mid") -> str:
        """
        Resets and starts a stateful interview session.
        Generates the first question.
        """
        if not self.session.target_role:
            return "Please select a target role first."
            
        self.session.interview_active = True
        self.session.interview_experience = experience_level
        self.session.interview_focus = focus_area
        self.session.interview_questions = []
        self.session.interview_answers = []
        self.session.interview_evaluations = []
        
        logger.info(f"Starting interview session for: {self.session.target_role}")
        
        first_question = self.interview_agent.generate_question(
            target_role=self.session.target_role,
            focus_area=focus_area,
            experience_level=experience_level
        )
        self.session.current_question = first_question
        self.session.interview_questions.append(first_question)
        
        return first_question

    def submit_interview_answer(self, user_answer: str) -> Tuple[str, Optional[str]]:
        """
        Submits candidate's answer for the current question, evaluates it, and generates the next question.
        Returns:
            Tuple[str, Optional[str]]: (Evaluation feedback, Next question / None if finished)
        """
        if not self.session.interview_active or not self.session.current_question:
            return "No active mock interview session found.", None
            
        # Security check on candidate's answer
        is_safe, cleaned_answer, error_msg = self.process_input(user_answer)
        if not is_safe:
            return error_msg, None
            
        self.session.interview_answers.append(cleaned_answer)
        
        # Evaluate current answer
        logger.info("Evaluating interview answer...")
        evaluation = self.interview_agent.evaluate_answer(
            target_role=self.session.target_role,
            question=self.session.current_question,
            user_answer=cleaned_answer
        )
        self.session.interview_evaluations.append(evaluation)
        
        # Decide if we ask another question (limit mock interview to 3 questions for a standard session)
        if len(self.session.interview_questions) >= 3:
            self.session.interview_active = False
            self.session.current_question = None
            summary_message = (
                f"{evaluation}\n\n"
                f"--- \n"
                f"### 🎉 Mock Interview Complete!\n"
                f"You have answered 3 questions. Check out the feedback above to refine your answers."
            )
            return summary_message, None
        else:
            # Generate next question
            logger.info("Generating next question...")
            next_question = self.interview_agent.generate_question(
                target_role=self.session.target_role,
                focus_area=self.session.interview_focus,
                experience_level=self.session.interview_experience
            )
            self.session.current_question = next_question
            self.session.interview_questions.append(next_question)
            return evaluation, next_question

    def review_resume(self, resume_text: str) -> str:
        """
        Runs the Resume review agent on the provided resume content.
        """
        if not self.session.target_role:
            return "Please select a target role first."
            
        # Security check (critical as resumes contain lots of PII like emails, phones, names)
        is_safe, cleaned_resume, error_msg = self.process_input(resume_text)
        if not is_safe:
            return error_msg
            
        context = {
            "target_role": self.session.target_role
        }
        
        logger.info("Running Resume Review...")
        feedback = self.resume_agent.run(cleaned_resume, context=context)
        return feedback
