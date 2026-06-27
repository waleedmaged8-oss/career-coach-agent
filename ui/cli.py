import sys
from typing import Optional, List
from core.orchestrator import Orchestrator
from core.config import TARGET_ROLES
import os

# ANSI Formatting helper
class Color:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

def print_header(title: str):
    """Prints a styled header."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'=' * 60}")
    print(f" {title.upper()}")
    print(f"{'=' * 60}{Color.RESET}")

def print_accent(text: str):
    """Prints highlighted info."""
    print(f"{Color.BLUE}{Color.BOLD}>>> {text}{Color.RESET}")

def get_multiline_input(prompt: str) -> str:
    """
    Collects multiple lines of text from the user until they write 'DONE' or submit an empty line.
    """
    print(prompt)
    print(f"{Color.YELLOW}(Type 'DONE' or press Enter on an empty line to finish input){Color.RESET}")
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "DONE" or (not line.strip() and len(lines) > 0):
                break
            if not line.strip() and len(lines) == 0:
                # Allow empty submit if it's the very first line (meaning skip/cancel)
                break
            lines.append(line)
        except KeyboardInterrupt:
            print(f"\n{Color.RED}Input cancelled.{Color.RESET}")
            return ""
    return "\n".join(lines)

class CareerCoachCLI:
    def __init__(self):
        self.orchestrator = Orchestrator()
        
    def start(self):
        """Main execution flow of the CLI application."""
        print(f"\n{Color.GREEN}{Color.BOLD}==================================================")
        print("    WELCOME TO THE AI CAREER COACH AGENT")
        print(f"=================================================={Color.RESET}")
        
        # Verify API Key exists
        from core.config import API_KEY
        if not API_KEY:
            print(f"{Color.RED}[!] WARNING: GEMINI_API_KEY environment variable is missing.{Color.RESET}")
            print("Please configure your API key to interact with the LLM agents.")
            print("You can set it in a .env file: GEMINI_API_KEY=AIzaSy...")
            print("Or export it in your shell: $env:GEMINI_API_KEY=\"AIzaSy...\"\n")
            
        if self.orchestrator.session.target_role:
            print(f"\n{Color.GREEN}✅ Previous session loaded successfully!{Color.RESET}")
            print(f"{Color.GREEN}Current Target Role: {self.orchestrator.session.target_role}{Color.RESET}")
        else:
            self.select_role_flow()

        self.main_menu_loop()
        

    def select_role_flow(self):
        """Flow for selecting the target career path."""
        print_header("Select Your Target Career Path")
        roles = list(TARGET_ROLES.keys())
        
        for idx, role in enumerate(roles, 1):
            print(f"  {Color.BOLD}{idx}. {role}{Color.RESET}")
            print(f"     {TARGET_ROLES[role]}")
            
        while True:
            try:
                choice = input(f"\nChoose role (1-{len(roles)}): ").strip()
                if not choice:
                    continue
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(roles):
                    selected_role = roles[choice_idx]
                    self.orchestrator.set_target_role(selected_role)
                    print(f"\n{Color.GREEN}🎯 Target Role set to: {Color.BOLD}{selected_role}{Color.RESET}")
                    break
                else:
                    print(f"{Color.RED}Invalid selection. Please choose a number between 1 and {len(roles)}.{Color.RESET}")
            except ValueError:
                print(f"{Color.RED}Please enter a valid number.{Color.RESET}")
            except (KeyboardInterrupt, EOFError):
                print(f"\n{Color.RED}Exiting...{Color.RESET}")
                sys.exit(0)

    def update_profile_flow(self):
        """Flow to update candidate's background details."""
        print_header("Update Your Professional Profile")
        
        experience = get_multiline_input(
            f"\n{Color.BOLD}1. Describe your professional and academic background:{Color.RESET}\n"
            f"(e.g., 'Bachelor in Physics, 2 years working as a Data Analyst at a retail company, write Python scripts daily')"
        )
        
        skills = get_multiline_input(
            f"\n{Color.BOLD}2. List your current technical skills and tools:{Color.RESET}\n"
            f"(e.g., 'SQL, Python, Pandas, Matplotlib, basic Git, Excel')"
        )
        
        self.orchestrator.update_profile(experience=experience, skills=skills)
        print(f"\n{Color.GREEN}✅ Professional Profile updated successfully!{Color.RESET}")

    def run_skill_gap_flow(self):
        """Runs the Skill Gap analysis."""
        print_header(f"Analyzing Skill Gaps for: {self.orchestrator.session.target_role}")
        
        # Check if profile is set
        if not self.orchestrator.session.current_skills or not self.orchestrator.session.current_experience:
            print(f"{Color.YELLOW}[!] Your profile details are incomplete.{Color.RESET}")
            confirm = input("Would you like to fill your profile now? (y/n): ").strip().lower()
            if confirm == 'y':
                self.update_profile_flow()
            else:
                print(f"{Color.BLUE}Proceeding with empty profile. Gaps may be less specific.{Color.RESET}")

        additional_info = input(f"\nAny specific projects or concerns you want to add? (Press Enter to skip): ").strip()
        
        print_accent("Analyzing skills against industry standards. Please wait...")
        analysis = self.orchestrator.run_skill_gap_analysis(additional_info)
        

        print("\n" + analysis)

        # Save report
        os.makedirs("outputs", exist_ok=True)

        with open("outputs/skill_gap.md", "w", encoding="utf-8") as f:
            f.write(analysis)

        print(f"\n{Color.GREEN}✅ Report saved to outputs/skill_gap.md{Color.RESET}")
        print(f"{Color.GREEN}✨ Gap analysis completed.{Color.RESET}")

    def run_roadmap_flow(self):
        """Generates the learning roadmap."""
        print_header(f"Generating learning roadmap for: {self.orchestrator.session.target_role}")
        
        # Check if gap analysis was already run
        if not self.orchestrator.session.skill_gaps:
            print(f"{Color.YELLOW}[!] No skill gap analysis is saved in this session.{Color.RESET}")
            confirm = input("Would you like to run the Skill Gap analysis first for better customization? (y/n): ").strip().lower()
            if confirm == 'y':
                self.run_skill_gap_flow()
                print_header("Generating Learning Roadmap")

        timeline = input(f"What is your target timeline? (e.g. '3 months, 15 hours/week' or press Enter for default): ").strip()
        additional_info = input(f"Any specific preferences? (e.g. 'Prefer python packages, no paid courses' or press Enter to skip): ").strip()
        
        print_accent("Creating your customized milestone-based roadmap. Please wait...")
        roadmap = self.orchestrator.run_learning_roadmap(additional_info, timeline=timeline or "Flexible")
        
        print("\n" + roadmap)

        # Save report
        os.makedirs("outputs", exist_ok=True)

        with open("outputs/roadmap.md", "w", encoding="utf-8") as f:
            f.write(roadmap)

        print(f"\n{Color.GREEN}✅ Report saved to outputs/roadmap.md{Color.RESET}")
        print(f"{Color.GREEN}✨ Learning roadmap generated successfully.{Color.RESET}")

    def run_mock_interview_flow(self):
        """Conducts an interactive, multi-turn interview prep session."""
        print_header(f"Stateful Mock Interview: {self.orchestrator.session.target_role}")
        
        focus_area = input("Enter a focus area (e.g., 'Machine Learning', 'SQL Joins', 'Behavioral', or press Enter for general): ").strip()
        experience = input("Enter experience level for questions ('Junior', 'Mid', 'Senior' - default: 'Mid'): ").strip()
        
        focus = focus_area if focus_area else None
        level = experience if experience else "Mid"
        
        print_accent(f"Starting interview session. Questions will target {level} level.")
        print(f"{Color.YELLOW}Note: The mock interview consists of 3 rounds. Answer each question as best as you can.{Color.RESET}\n")
        
        current_question = self.orchestrator.start_interview_session(focus_area=focus, experience_level=level)
        
        question_count = 1
        while current_question:
            print(f"\n{Color.BLUE}{Color.BOLD}Question {question_count}:{Color.RESET}")
            print(f"{Color.BOLD}{current_question}{Color.RESET}")
            
            user_answer = get_multiline_input(f"\n{Color.CYAN}Your Answer:{Color.RESET}")
            if not user_answer.strip():
                print(f"{Color.RED}Answer cannot be empty. Skipping question...{Color.RESET}")
                # End interview or continue? We can try to submit empty or just break
                break
                
            print_accent("Evaluating your response and generating next step...")
            feedback, next_question = self.orchestrator.submit_interview_answer(user_answer)
            
            print_header(f"Feedback for Question {question_count}")
            print(feedback)
            
            current_question = next_question
            question_count += 1

    def run_resume_review_flow(self):
        """Flow for reviewing resumes."""
        import os

        print_header(f"Resume Review for: {self.orchestrator.session.target_role}")

        choice = input(
            "\nChoose input method:\n"
            "1. Paste resume text\n"
            "2. Load from text file (.txt)\n"
            "Choice (1/2): "
        ).strip()

        if choice == "2":
            path = input("Enter resume file path: ").strip().strip('"')

            if not os.path.exists(path):
                print(f"{Color.RED}File not found.{Color.RESET}")
                return

            try:
                with open(path, "r", encoding="utf-8") as f:
                    resume_text = f.read()
            except UnicodeDecodeError:
                with open(path, "r", encoding="cp1252") as f:
                    resume_text = f.read()

        else:
            print(f"{Color.YELLOW}Paste your resume text below.{Color.RESET}")
            resume_text = get_multiline_input("")

        if not resume_text.strip():
            print(f"{Color.RED}Resume content is empty. Returning to menu.{Color.RESET}")
            return

        print_accent("Reviewing resume structure, phrasing, and keywords. Please wait...")

        feedback = self.orchestrator.review_resume(resume_text)

        print_header("Resume Review Feedback")
        print(feedback)

        # Save report
        os.makedirs("outputs", exist_ok=True)

        with open("outputs/resume_review.md", "w", encoding="utf-8") as f:
            f.write(feedback)

        print(f"\n{Color.GREEN}✅ Report saved to outputs/resume_review.md{Color.RESET}")
        
        

    def main_menu_loop(self):
        """Displays main menu choices and handles input routing."""
        while True:
            print_header(f"Main Menu - Current Goal: {self.orchestrator.session.target_role}")
            print(f"  {Color.BOLD}1.{Color.RESET} Set/Update Profile Details (Skills, Background)")
            print(f"  {Color.BOLD}2.{Color.RESET} Perform Skill Gap Analysis")
            print(f"  {Color.BOLD}3.{Color.RESET} Generate Learning Roadmap")
            print(f"  {Color.BOLD}4.{Color.RESET} Stateful Mock Interview Practice (3 Rounds)")
            print(f"  {Color.BOLD}5.{Color.RESET} Review Resume for ATS & Phrasing")
            print(f"  {Color.BOLD}6.{Color.RESET} Change Target Role / Career Goal")
            print(f"  {Color.BOLD}7.{Color.RESET} Exit")
            
            choice = input(f"\nSelect an option (1-7): ").strip()
            if not choice:
                continue
                
            try:
                if choice == "1":
                    self.update_profile_flow()
                elif choice == "2":
                    self.run_skill_gap_flow()
                elif choice == "3":
                    self.run_roadmap_flow()
                elif choice == "4":
                    self.run_mock_interview_flow()
                elif choice == "5":
                    self.run_resume_review_flow()
                elif choice == "6":
                    self.select_role_flow()
                elif choice == "7":
                    print(f"\n{Color.GREEN}Good luck on your career journey! Goodbye.{Color.RESET}")
                    break
                else:
                    print(f"{Color.RED}Invalid option. Please choose between 1 and 7.{Color.RESET}")
            except Exception as e:
                print(f"\n{Color.RED}An unexpected error occurred during execution: {e}{Color.RESET}")
                import traceback
                traceback.print_exc()
            
            input(f"\n{Color.YELLOW}Press Enter to return to the Main Menu...{Color.RESET}")
