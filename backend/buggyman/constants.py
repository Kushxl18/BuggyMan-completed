import os
from pathlib import Path

# Load backend/.env if present
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and not os.getenv(k):
                        os.environ[k] = v
    except Exception:
        pass

# BugBytes Rewards
EASY_BUGBYTE_REWARD = 10
MEDIUM_BUGBYTE_REWARD = 20
HARD_BUGBYTE_REWARD = 35
FIRST_ATTEMPT_BONUS = 5
FULL_TEST_PASS_BONUS = 5

# AI Hint Costs
HINT_COSTS = {
    1: 5,   # Level 1: Conceptual Hint (5 BugBytes)
    2: 10,  # Level 2: Directional Hint (10 BugBytes)
    3: 15   # Level 3: Detailed Hint (15 BugBytes)
}

# Groq AI Service Configuration
def get_groq_api_key():
    return os.getenv('GROQ_API_KEY', '').strip()

def get_groq_model():
    return os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b').strip()

def get_groq_base_url():
    return os.getenv('GROQ_BASE_URL', 'https://api.groq.com/openai/v1').strip()

GROQ_API_KEY = get_groq_api_key()
GROQ_MODEL = get_groq_model()
GROQ_BASE_URL = get_groq_base_url()
