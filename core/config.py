import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CareerCoach")

# Load environment variables from .env file
load_dotenv()

# Gemini Configurations
DEFAULT_MODEL = "gemini-2.5-flash"
API_KEY = os.environ.get("GEMINI_API_KEY")

_client = None

def get_genai_client():
    """
    Initializes and returns the Gemini GenAI Client.
    Fails gracefully with a helpful message if the API key is missing.
    """
    global _client
    if _client is not None:
        return _client
    
    if not API_KEY:
        logger.error("GEMINI_API_KEY environment variable is not set. Please set it to use the AI features.")
        print("\n[!] WARNING: GEMINI_API_KEY environment variable is not set.")
        print("Please create a .env file or set the environment variable:")
        print("  On Windows Powershell: $env:GEMINI_API_KEY=\"your_key_here\"")
        print("  On Bash/Linux/macOS: export GEMINI_API_KEY=\"your_key_here\"\n")
        # We don't exit here to allow offline checks/testing, but client calls will fail.
        return None
        
    try:
        from google import genai
        _client = genai.Client(api_key=API_KEY)
        return _client
    except ImportError:
        logger.error("Failed to import 'google-genai'. Please run: pip install google-genai")
        print("\n[!] Error: 'google-genai' package is not installed. Please run: pip install -r requirements.txt\n")
        return None
    except Exception as e:
        logger.error(f"Error initializing Google GenAI Client: {e}")
        return None

# Target careers defined in requirement
TARGET_ROLES = {
    "Data Analyst": "Focuses on querying database (SQL), data cleaning, descriptive statistics, visualization (Tableau, PowerBI), and business communication.",
    "Data Scientist": "Focuses on statistics, predictive modeling, machine learning algorithms, programming (Python/R), and storytelling with data.",
    "AI Engineer": "Focuses on integrating large language models (LLMs), building prompt chains, RAG (Retrieval-Augmented Generation), fine-tuning APIs, and building GenAI applications.",
    "Machine Learning Engineer": "Focuses on ML pipelines, model deployment, MLOps, deep learning architectures, scalability, and optimizing training/inference."
}
